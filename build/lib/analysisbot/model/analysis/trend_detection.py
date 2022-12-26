import numpy as np
import pandas as pd
import seaborn as sns
# import spacy
import os
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from pymcdm import methods as mcdm_methods
from pymcdm import weights as mcdm_weights
from sklearn import linear_model

from analysisbot.logging.logger import _logger
from analysisbot.database.mongodb import MongoManager


class TrendDetection:
    mongodb = MongoManager.get_instance()
    
    @staticmethod
    def token_to_word(ids, as_dict=True):
        '''Метод для преобразования токена(id слова) в само слово в виде строки'''
        word = ""
        for id in ids.split('_'):
            doc = MongoManager.find_data('dictionary', {'_id': int(id)})
            res =  doc['word']
            if res is None:
                _logger.exception("[TrendDetection] id was not found in database")
                return {id: "None"}
            word += res
            word += " "
        if as_dict: return {ids: word}
        else: return word
    
    
    @staticmethod
    def typed_read_csv(path: str) -> pd.DataFrame:
        '''Метод для чтения csv и приведения столбца с датами к типу datetime'''
        try:
            df = pd.read_csv(
                path,
                dtype={'token':object, 'date':object, 'frequency':int, 'views':int, 'reactions':int},
                index_col=0)
            df['date'] = pd.to_datetime(df['date'])
        except Exception as e:
            print(e)
            df = None
        
        return df
    
    
    @staticmethod
    def sum_merged_data(source_list, month: datetime):
        """sum_merged_data
        Соединяет предобработанные данные для всех источников за конкретный месяц в одну таблицу, суммирует данные для каждого токена

        Args:
            source_list (dict[list[str]]): список источников, которые надо прочитать в формате {"type": {'telegram": ["Reddit", "investorbiz" ...], "vk":["nrnews"]}}
            month (datetime): За какой месяц прочитать и слить в одну таблицу данные данные

        Returns:
            pd.DataFrame|None: таблица, где для каждого источника суммарная статистика за месяц
        """        
        merged_df = None
             
        for type in source_list.keys():
            for source in source_list[type]:
                path = "./storage/data/{}/{}/{}/{}stats.csv".format(
                    type, source, month.year, str(month.month).zfill(2))
                
                new_df = TrendDetection.typed_read_csv(path)
                if new_df is not None:
                    if (merged_df is None):
                        merged_df = new_df
                    else:
                        merged_df = pd.concat([merged_df, new_df], ignore_index=True)
                        merged_df.reset_index(inplace=True, drop=True)
        try:
            # print(len(merged_df.index))
            merged_df = merged_df.groupby(['token']).agg({'frequency':'sum', 'views':'mean', 'reactions':'mean'})
            merged_df['date'] = month
        except Exception as e:
            _logger.warning(e, month)
        return merged_df
    
    
    @staticmethod
    def mcdm_score(df: pd.DataFrame):
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
        _logger.info('full_df merged')
        del df
        full_df.fillna(0, inplace=True)
        
        data = full_df[['frequency', 'views', 'reactions']].to_numpy()
        # calculating the score
        weights = np.array([0.5, 0.25, 0.25])
        types = np.array([1, 1, 1])
        topsis = mcdm_methods.TOPSIS() #has a normalization_funciton argument which is minmax_normalization by default
        score: np.ndarray = topsis(data, weights, types)
        del data
        res = pd.DataFrame(data=score.reshape(tokens.shape[0], dates.shape[0]).T, columns=tokens) 
        res.insert(loc=0, column='date', value=dates)
        res = res.set_index('date')
        _logger.info('score calculated')
        return res
    
    @staticmethod
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
        _logger.info('full_df merged')
        del df
        full_df.fillna(0, inplace=True)
        score = full_df['frequency'].to_numpy()
        # score = np.where(score==0, 1, score)
        res = pd.DataFrame(data=score.reshape(tokens.shape[0], dates.shape[0]).T, columns=tokens) 
        res.insert(loc=0, column='date', value=dates)
        res = res.set_index('date')
        
        _logger.info('score calculated')
        return res   
        
        
    @staticmethod
    def chunking(sources, window_end_period:datetime, history:int, remerge:bool=True, mcdm:bool=False) -> pd.DataFrame:
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
        sum_by_month = None
        
        for date in pd.date_range(end=window_end_period, freq='M', periods=history):
            path = f'./storage/chunks/{date.year}/{str.zfill(str(date.month),2)}chunk.csv'
            
            if remerge:
                window_df = TrendDetection.sum_merged_data(sources, date)
                os.makedirs(f'./storage/chunks/{date.year}', exist_ok=True)
                window_df.to_csv(path)
            else:
                window_df = pd.read_csv(path, index_col=0)
            # print('size: ', len(window_df.index))
            if(len(window_df)!=0):
                if sum_by_month is None:
                    sum_by_month = window_df
                else:
                    sum_by_month = pd.concat([sum_by_month, window_df])

        sum_by_month.fillna(0, inplace=True)
        sum_by_month.reset_index(inplace=True)
        # print(sum_by_month.head(5).to_string())
        if mcdm:
            return TrendDetection.mcdm_score(sum_by_month)
        else:
            sum_by_month.drop(['views', 'reactions'], axis=1, inplace=True)
            sum_by_month.loc[sum_by_month['frequency']==0, 'frequency']=1
            # print(sum_by_month)
            return TrendDetection.rearrange_freq_only(sum_by_month)


    @staticmethod
    def mean_differance(sources: dict, current_date, period:int, remerge=True, mcdm=False) -> pd.DataFrame:
        sum_means = TrendDetection.chunking(sources, current_date, period, remerge, mcdm)
        sum_means = sum_means.mean(axis=0).to_frame(name='previous')
        _logger.info('sum_means done')

        cur_mean = TrendDetection.chunking(sources, current_date+timedelta(days=30), 1, remerge, mcdm)
        cur_mean = cur_mean.mean(axis=0).to_frame(name='current')
        _logger.info('current_mean done')

        compare = sum_means.join(cur_mean, how='outer')
        del sum_means
        del cur_mean
        compare.fillna(0.0, inplace=True)
        
        return compare


    @staticmethod
    def mean_score_ratio(df: pd.DataFrame, zero_replace=1):
        '''Сортировка по отношению значений'''
        df['growth'] = df.apply(lambda x: x[1]/x[0] if x[0]!=0 else x[1]/zero_replace, axis=1)
        # print(f'Отношение значений, \nделение на ноль заменяем на {zero_replace}')
        # print()
    

    @staticmethod
    def rename_columns(df: pd.DataFrame):
        words = map(TrendDetection.token_to_word, df.columns)
        new_columns = {}
        for i in words:
            new_columns.update(i) 
        df.rename(columns=new_columns, inplace=True)


    @staticmethod
    def read_pkl(path, ref):
        '''Чтение pickle исходника, поиск конкретного поста'''
        l_raw = pd.read_pickle(path)
        if l_raw == []:
            _logger.warning(f'Empty source file {path}')
            return []
        # print(l_raw)
        else:
            raw = pd.DataFrame(l_raw)
            raw['ref'] = raw['ref'].astype(object)
        # print(raw.head(3).to_string())
        
            found = raw.loc[raw['ref']==ref]
            # txt = found['text'].to_numpy()
            try:
                return found['ref'].tolist()[0], found['date'].tolist()[0], found['text'].tolist()[0]
            except:
                return found['ref'].tolist(), found['date'].tolist(), found['text'].tolist()

    
    @staticmethod     
    def usage(token, p_unique:set, start_date):
        '''Поиск использований токена в тексте'''
        date = start_date
        try:
            df = pd.read_csv(f'./storage/ref.csv', names=['token', 'year', 'month', 'path','ref'], dtype={'token':object, 'year':int, 'month':int, 'path':object, 'ref':object})
            # df.reset_index(inplace=True)
        except Exception as e:
            print(token, end=' __ ')
            print(e)
            return [{'path': "_",'ref': "_", 'date':"_", 'text':"_"}]
        df = df.loc[(df['token']==str(token)) & (df['year']==date.year), ['token', 'month', 'path', 'ref']]
        docs: pd.DataFrame = df.loc[(df['month']==date.month) | (df['month']==date.month-1), ['path', 'ref']]
        docs.reset_index(inplace=True)
        del df
        if len(docs)==0:
            return [["Not found", 'not found']]
        res = []
        for i,doc in docs.iterrows():
            if not doc['ref'] in p_unique:
                path = doc['path']
                r, d, t = TrendDetection.read_pkl(path+"raw.pkl", doc['ref'])
                res.append({'path':path,'ref':r, 'date':d, 'text':t})
                p_unique.add(doc['ref'])
        del docs
        return res

    #! ==========================================================================================================
    @staticmethod
    def merge_one_token_data(source_dict: dict, token, month: datetime):
        merged_df = None
        for type in source_dict.keys():
            for source in source_dict[type]:
                path = "./storage/data/{}/{}/{}/{}stats.csv".format(
                    type, source, month.year, str(month.month).zfill(2))
                
                new_df = TrendDetection.typed_read_csv(path)
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
    
    
    @staticmethod
    def chunking_one(sources, token, end_date:datetime, history:int, remerge:bool=True, mcdm:bool=False):
        sum_by_month = None
        for end in pd.date_range(end=end_date, freq='M', periods=history):
            path = f'./storage/chunks/{end.year}/{str.zfill(str(end.month),2)}chunk.csv'
            if remerge:
                window_df = TrendDetection.merge_one_token_data(sources, token, end)
            else:
                window_df = pd.read_csv(path, index_col=0)
            if window_df is not None:
                if(len(window_df)!=0):
                    if sum_by_month is None:
                        sum_by_month = window_df
                    else:
                        sum_by_month = pd.concat([sum_by_month, window_df])
            else:
                window_df = pd.DataFrame({'token': token, 'frequency': 0, 'views':0.0, 'reactions':0.0})
                if sum_by_month is None:
                        sum_by_month = window_df
                else:
                    sum_by_month = pd.concat([sum_by_month, window_df])

        if sum_by_month is not None:
            sum_by_month.fillna(0, inplace=True)
            sum_by_month.reset_index(inplace=True)
            if mcdm:
                return TrendDetection.mcdm_score(sum_by_month)
            else:
                sum_by_month.drop(['views', 'reactions'], axis=1, inplace=True)
                return TrendDetection.rearrange_freq_only(sum_by_month)
        else:
            return None
        
        
    def one_token_graph(sources, current_date, period, token):
        token_stats = TrendDetection.chunking_one(sources, token, current_date+timedelta(days=30), period)
        plt.figure(clear=True, figsize=(15,8))
        sns.set_theme(style="darkgrid")
        sns.lineplot(token_stats)
        plt.xticks(rotation=15)
        plt.savefig(f'storage/img/img_{token}.png')
        _logger.warning(f"img_{token} saved")
        plt.close()
        
        return token_stats
    
    def top_token_stats(stats):
        plt.figure(clear=True, figsize=(15,8))
        sns.set_theme(style="darkgrid")
        sns.lineplot(stats, dashes=False)
        plt.xticks(rotation=15)
        plt.savefig('storage/img/all.png')
        plt.close()
    
    #! ==========================================================================================================
    
    
    @staticmethod
    def get_top_data(source_dict: dict, process: list, period: int, trend_window: int, number:int, seg_type):
        start_date = datetime.now()
        
        df = TrendDetection.mean_differance(source_dict, start_date, period, remerge=True, mcdm=False)
        TrendDetection.mean_score_ratio(df, 1)
        
        df.sort_values(by='growth', ascending=False, inplace=True)
        df['word'].to_csv(f'{seg_type}_dict.csv')
        df = df.iloc[:number]
        df['word'] = df.index.map(lambda x: TrendDetection.token_to_word(x, False))
        df = df[['word', 'previous', 'current', 'growth']]
        all_stats: pd.DataFrame = None
        os.makedirs('storage/img', exist_ok=True)
        for tok in df.index.to_numpy():
            # print(tok)
            u = TrendDetection.usage(tok, set(), start_date)
            with open(f'storage/usage/usage_{tok}.json', 'w', encoding='utf-8') as file:
                pd.DataFrame(u).to_json(file, orient='records', date_format='iso', indent=4, force_ascii=False)
            
            
            one_stat = TrendDetection.one_token_graph(source_dict, start_date, period, tok)
            print(tok, "img")
            print(one_stat)
            if all_stats is None:
                all_stats = one_stat
            else:
                all_stats = pd.concat([all_stats, one_stat])
                print(one_stat)
            
            
        print(all_stats.info())
        TrendDetection.top_token_stats(all_stats)
            
        print(df.round(2))
        print(df.info())
        return df.round(2)
    
    
   