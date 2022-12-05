import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from pymcdm import methods as mcdm_methods
from pymcdm import weights as mcdm_weights
from sklearn import linear_model
from typing import Optional
from myapp.database.mongodb import MongoManager
from myapp.model.analysis.trend_detection import TrendDetection
from myapp.logging.logger import _logger


def token_to_word(ids, as_dict=True):
        '''Метод для преобразования токена(id слова) в само слово в виде строки'''
        word = ""
        for id in str(ids).split('_'):
            doc = MongoManager.find_data('dictionary', {'_id': int(id)})
            if doc is None:
                print("!!!!!!!! [TrendDetection] id was not found in database")
                return {id: "None"}
            res =  doc['word']
            word += res
            word += " "
        if as_dict: return {ids: word}
        else: return word
        
def typed_read_csv(path: str) -> pd.DataFrame:
        '''Метод для чтения csv и приведения столбца с датами к типу datetime'''
        try:
            df = pd.read_csv(
                path,
                dtype={'token':object, 'date':object, 'frequency':int, 'views':int, 'reactions':int},
                index_col=0)
            df['date'] = pd.to_datetime(df['date'])
            # print(path, len(df.index))
        except Exception as e:
            # print(e)
            df = None
        return df
    
def merge_one_token_data(source_dict: dict, token, month: datetime):
    merged_df: pd.DataFrame = None
    for type in source_dict.keys():
        for source in source_dict[type]:
            path = "./storage/data/{}/{}/{}/{}stats.csv".format(
                type, source, month.year, str(month.month).zfill(2))
            
            new_df = typed_read_csv(path)
            # print(new_df.head(5).to_string())
            if new_df is not None:
                new_df = new_df.loc[new_df['token']==token]
                if (merged_df is None):
                    merged_df = new_df
                else:
                    merged_df = pd.concat([merged_df, new_df], ignore_index=True)
                    merged_df.reset_index(inplace=True, drop=True)
    try:
        # print(len(merged_df.index))
        merged_df = merged_df.groupby(['token']).agg({'frequency':'sum', 'views':'mean', 'reactions':'mean'})
        # print(merged_df.head(5).to_string())
        merged_df['date'] = month
    except Exception as e:
         _logger.debug(e)
    return merged_df
            
    
def sum_merged_data(source_list: dict, month: datetime):
    """sum_merged_data
    Соединяет предобработанные данные для всех источников за конкретный месяц в одну таблицу, суммирует данные для каждого токена

    Args:
        source_list (dict[list[str]]): список источников, которые надо прочитать в формате {"type": {'telegram": ["Reddit", "investorbiz" ...], "vk":["nrnews"]}}
        month (datetime): За какой месяц прочитать и слить в одну таблицу данные данные

    Returns:
        pd.DataFrame|None: таблица, где для каждого источника суммарная статистика за месяц
    """        
    merged_df: pd.DataFrame = None
    for type in source_list.keys():
        for source in source_list[type]:
            path = "./storage/data/{}/{}/{}/{}stats.csv".format(
                type, source, month.year, str(month.month).zfill(2))
            
            new_df = typed_read_csv(path)
            # print(new_df.head(5).to_string())
            if new_df is not None:
                if (merged_df is None):
                    merged_df = new_df
                else:
                    merged_df = pd.concat([merged_df, new_df], ignore_index=True)
                    merged_df.reset_index(inplace=True, drop=True)
    try:
        # print(len(merged_df.index))
        merged_df = merged_df.groupby(['token']).agg({'frequency':'sum', 'views':'mean', 'reactions':'mean'})
        # print(merged_df.head(5).to_string())
        merged_df['date'] = month
        # merged_df.loc[merged_df['frequency']==0, 'frequency']=1
        # print(merged_df['frequency'].min())
        # print(merged_df.head(5).to_string())
    except Exception as e:
         _logger.debug(e)
    return merged_df


def rearrange_freq_only(df):
    '''Преобразование таблицы в вид как в mcdm_score, но с ипользованием только частоты (без view, reactions)'''
    tokens = df['token'].unique()
    tokens.sort()
    dates = df['date'].unique()
    dates.sort()
    unique_tokens = pd.DataFrame(tokens, columns=['token'])
    unique_dates = pd.DataFrame(dates, columns=['date'])
        
    full_df = unique_tokens.merge(unique_dates, how='cross')
    del unique_tokens
    del unique_dates
    full_df = full_df.merge(df, how='left')
    # _logger.info('full_df merged')
    del df
    full_df.fillna(0, inplace=True)
    score = full_df['frequency'].to_numpy()
    score = np.where(score==0, 1, score)
    res = pd.DataFrame(data=score.reshape(tokens.shape[0], dates.shape[0]).T, columns=tokens) 
    res.insert(loc=0, column='date', value=dates)
    res = res.set_index('date')
    
    # _logger.info('score calculated')
    return res    


def chunking(sources, token, end_date:datetime, history:int, remerge:Optional[bool]=False, mcdm:Optional[bool]=True):
    """chunking _summary_

    Args:
        sources (_type_): список источников, которые надо прочитать в формате {"type": {'telegram": ["Reddit", "investorbiz" ...], "vk":["nrnews"]}} [нужны для sum_merged_data]
        end_date (datetime): _description_
        history (int): число месяцев, за которые смотреть историю
        remerge (Optional[bool], optional): True-заново расчитать чанки. False-прочитать имеющиеся. Defaults to False.
        mcdm (Optional[bool], optional): True-мультикритериальный score. False-использовать только частоту. Defaults to True.

    Returns:
        pd.DataFrame|None
    """    
    sum_by_month: pd.DataFrame = None
    # for start, end in zip(pd.date_range(end=datetime.now().replace(month=10), freq='M', periods=history), pd.date_range(end=datetime.now(), freq='M', periods=history)):
    for end in pd.date_range(end=end_date, freq='M', periods=history):
        # print(end)
        path = f'./storage/chunks/{end.year}/{str.zfill(str(end.month),2)}chunk.csv'
        # print(end)
        if remerge:
            window_df = merge_one_token_data(sources, token, end)
            if window_df is not None:
                window_df.to_csv(path)
        else:
            window_df = pd.read_csv(path, index_col=0)
        # print('size: ', len(window_df.index))
        if window_df is not None:
            if(len(window_df)!=0):
                if sum_by_month is None:
                    sum_by_month = window_df
                else:
                    sum_by_month = pd.concat([sum_by_month, window_df])

    if sum_by_month is not None:
        sum_by_month.fillna(0, inplace=True)
        sum_by_month.reset_index(inplace=True)
        # print(sum_by_month.head(5).to_string())
        if mcdm:
            return TrendDetection.mcdm_score(sum_by_month)
        else:
            sum_by_month.drop(['views', 'reactions'], axis=1, inplace=True)
            #! sum_by_month.loc[sum_by_month['frequency']==0, 'frequency']=1
            # print(sum_by_month)
            return rearrange_freq_only(sum_by_month)
    else:
        return None

   

def calc_meams_df(sources, token, start_date: datetime, period:int, remerge=False, mcdm=True):
    """calc_meams_df _summary_
    Счиатет среднее для каждого токена за всю историю и за последний месяц

    Args:
        sources (_type_): список источников, которые надо прочитать в формате {"type": {'telegram": ["Reddit", "investorbiz" ...], "vk":["nrnews"]}} [нужны для sum_merged_data]
        history (int): число месяцев, за которые смотреть историю
        remerge (Optional[bool], optional): True-заново расчитать чанки. False-прочитать имеющиеся. Defaults to False.
        mcdm (Optional[bool], optional): True-мультикритериальный score. False-использовать только частоту. Defaults to True.

    Returns:
        pd.DataFrame: таблица средних за историю
        pd.DataFrame: таблица средних за последний месяц
    """    
    # print('history_________________________________________________')
    sum_means = chunking(sources, token, start_date, period, remerge, mcdm)
    if sum_means is not None:
    # sum_means.replace(0.0, 1.0, inplace=True)
        min_score = sum_means.min().min()
        max_score = sum_means.max().max()
        sum_means = sum_means.mean(axis=0).to_frame(name='previous') #!!!!!!!
    else: sum_means=pd.DataFrame({'previous': 0.0}, index=[token])
    # _logger.info('period_means done')

    # cur_mean = chunking(sources, datetime.now()+timedelta(days=30), 1, remerge, mcdm)
    # print('current_________________________________________________')
    cur_mean = chunking(sources, token, start_date+timedelta(30), 1, remerge, mcdm)
    if cur_mean is not None:
        cur_mean.replace(0.0, 1.0, inplace=True)
        min_score = min(min_score, cur_mean.min().min())
        max_score = max(max_score, cur_mean.max().max())
        amp = max_score - min_score
        cur_mean = cur_mean.mean(axis=0).to_frame(name='current')
    else: cur_mean=pd.DataFrame({'current': 0.0}, index=[token])
    # cur_mean.replace(0.0, 1.0, inplace=True)
    # cur_mean = cur_mean.to_frame(name='current')
    # print('current done')

    compare = sum_means.join(cur_mean, how='outer')
    del sum_means
    del cur_mean
    # compare.to_csv('compare.csv')
    compare.fillna(1.0, inplace=True) #!!!!!!
    # compare.loc[compare['previous']]
    return compare



def mean_score_differance_with_koeff(df: pd.DataFrame, amp ):
    '''Сортировка по разности средних значений делить на коэффициент масштаба'''
    df['growth'] = (df['current'] - df['previous'])*(df['current']/amp)
    print('Разность средних значений делить на коэффициент масштаба, \nкоэф.- максимальная амплитуда')
    print()
    
def mean_score_differance(df: pd.DataFrame):
    '''Сортировка по разности средних значений'''
    df['growth'] = (df['current'] - df['previous'])
    print('Разность средних значений')
    print()
    
def mean_score_ratio(df: pd.DataFrame, zero_replace=0.001):
    '''Сортировка по отношению значений'''
    df['growth'] = df.apply(lambda x: x[1]/x[0] if x[0]!=0 else x[1]/zero_replace, axis=1)
    # print(f'Отношение значений, \nделение на ноль заменяем на {zero_replace}')
    # print()
 
 
def read_pkl(path, ref):
    '''Чтение pickle исходника, поиск конкретного поста'''
    l_raw = pd.read_pickle(path)
    # print(l_raw)
    raw = pd.DataFrame(l_raw)
    # raw['ref'] = raw['ref'].astype(object)
    # print(raw.head(3).to_string())
    if l_raw == []:
        #  _logger.debug(f'Empty source file {path}')
        return []
    else:
        found = raw.loc[raw['ref']==str(ref)]
        # txt = found['text'].to_numpy()
        return found['ref'].tolist()[0], found['date'].tolist()[0], found['text'].tolist()[0]

           
def usage(token, p_unique:set, start_date):
    '''Поиск использований токена в тексте'''
    # date = datetime.today() - timedelta(days= 10)
    date = start_date
    try:
        df = pd.read_csv(f'./storage/ref.csv', names=['token', 'year', 'month', 'path','ref'], dtype={'token':object, 'year':int, 'month':int, 'path':object, 'ref':object})
        # df.reset_index(inplace=True)
    except Exception as e:
        print(token, end=' __ ')
        print(e)
        return [["Not found", 'not found']]
    df = df.loc[(df['token']==str(token)) & (df['year']==date.year), ['token', 'month', 'path', 'ref']]
    docs: pd.DataFrame = df.loc[(df['month']==date.month) | (df['month']==date.month-1), ['path', 'ref']]
    docs.reset_index(inplace=True)
    del df
    # docs: list = MongoManager.find_random('token_ref', {'token': token, 'year': date.year, 'month': date.month})
    # print(len(docs))
    if len(docs)==0:
        return [["Not found", 'not found']]
    res = []
    for i,doc in docs.iterrows():
        if not doc['ref'] in p_unique:
            path = doc['path']
            # path = path[:-2]
            # path += '11'
            r, d, t = read_pkl(path+"raw.pkl", doc['ref'])
            res.append({'path':path,'ref':r, 'date':d, 'text':t})
            p_unique.add(doc['ref'])
    del docs
    return res


if __name__=="__main__":
    
    
    
    from dateutil import relativedelta
    sources = {'telegram': ['FinZoZhExpert', 'investorbiz', 'Reddit','tinkoff_invest_official', 'coinkeeper', 'vcnews'],
                  'vk': ['nrnews24', 'noboring_finance'],
                  'tinkoff_journal': ['business-russia', 'crisis','edu-news', 'opinion']}    
    start_date = datetime.now()-timedelta(days=2)
    # p = pd.read_pickle('./storage/data/telegram/FinZoZhExpert/2022/11raw.pkl')
    # pd.DataFrame(p).to_csv('pickle.csv')
    token = '813'
    
    #!------------------------------------------------------------------
    
    start_date = datetime.now()-relativedelta.relativedelta(month=1, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    # mean_score_differance_with_koeff(df )
    # mean_score_differance(df)
    mean_score_ratio(df, 1)
    
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]
    # for tok in df.index.to_numpy():
    #     u = usage(tok, set(), start_date)
    #     with open(f'usage_{tok}.json', 'w', encoding='utf-8') as file:
    #         pd.DataFrame(u).to_json(file, orient='records', date_format='iso', indent=4, force_ascii=False)
        # pd.DataFrame(u).to_csv(f"{tok}.csv")
    # print(df.info())
    df['month'] = start_date.date()
    print(df.round(2).to_string(header=True))
    
    #!-------------
    start_date = datetime.now()-relativedelta.relativedelta(month=2, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=3, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=4, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=5, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=6, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=7, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=8, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=9, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    start_date = datetime.now()-relativedelta.relativedelta(month=10, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    
    
    start_date = datetime.now()-relativedelta.relativedelta(month=11, days=2)
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    mean_score_ratio(df, 1)
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]

    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))
    
    # start_date = datetime.now()-relativedelta.relativedelta(month=12, days=2)
    # df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    
    # mean_score_ratio(df, 1)
    
    # df.sort_values(by='growth', ascending=False, inplace=True)
    # df = df.iloc[:10]
    # df['word'] = df.index.map(lambda x: token_to_word(x, False))
    # df = df[['word', 'previous', 'current', 'growth']]

    # df['month'] = start_date.date()
    # print(df.round(2).to_string(header=False))
    df  = calc_meams_df(sources, token, start_date, 12,remerge=True, mcdm=False)
    # print()
    
    # mean_score_differance_with_koeff(df )
    # mean_score_differance(df)
    mean_score_ratio(df, 1)
    
    
    df.sort_values(by='growth', ascending=False, inplace=True)
    df = df.iloc[:10]
    df['word'] = df.index.map(lambda x: token_to_word(x, False))
    df = df[['word', 'previous', 'current', 'growth']]
    for tok in df.index.to_numpy():
        u = usage(tok, set(), start_date)
        with open(f'usage_{tok}.json', 'w', encoding='utf-8') as file:
            pd.DataFrame(u).to_json(file, orient='records', date_format='iso', indent=4, force_ascii=False)
        # pd.DataFrame(u).to_csv(f"{tok}.csv")
    # print(df.info())
    df['month'] = start_date.date()
    print(df.round(2).to_string(header=False))