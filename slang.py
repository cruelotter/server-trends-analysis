import os
import pandas as pd
from datetime import datetime
from itertools import combinations
from analysisbot.database.mongodb import MongoManager


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


def token_to_word(ids, as_dict=True):

    '''Метод для преобразования токена(id слова) в само слово в виде строки'''
    word = ""
    doc = MongoManager.find_data('dictionary', {'_id': int(ids)})
    res =  doc['word']
    if res is None:
        print("[TrendDetection] id was not found in database")
        return {id: "None"}
    word += res
    if as_dict: return {ids: word}
    else: return word
        
        
def merge_one_token_data(source_dict: dict, token, month: datetime):
    merged_df = None
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
        # print(merged_df)
        # print(month, token)
        # print("===================================\n")
        # merged_df['date'] = month
    except Exception as e:
        print(e)
    return merged_df

source_dict = {'telegram': ['FinZoZhExpert', 'investorbiz','Reddit','tinkoff_invest_official','coinkeeper','vcnews', 'dvachannel','TochkaUP','BizLike','melfm', 'hour25','mashmoyka','fontankaspb','Taygainfo'],
'vk': ['nrnews24','noboring_finance','public28905875','public29534144','melfmru','club66678575','rambler']}
# 16,https://journal.tinkoff.ru/flows/crisis/,1,50,50,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 17,https://journal.tinkoff.ru/flows/edu-news/,1,50,50,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 18,https://journal.tinkoff.ru/flows/opinion/,1,50,50,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 19,https://journal.tinkoff.ru/flows/hobby/,1,40,60,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 20,https://journal.tinkoff.ru/flows/maternity-leave/,1,40,60,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 21,https://journal.tinkoff.ru/flows/love-hate-kids-purchase/,1,40,60,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 22,https://journal.tinkoff.ru/flows/baby/,1,40,60,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 23,https://journal.tinkoff.ru/flows/business-opinion/,1,50,50,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
# 24,https://journal.tinkoff.ru/flows/goskontrol/,1,50,50,{"-18":12.5;"18-21":12.5;"21-24":12.5;"24-27":12.5;"27-30":12.5;"30-35":12.5;"35-45":12.5;"45+":12.5},ALL
        
# mongodb = MongoManager.get_instance()
# seg1 = pd.read_csv('segment_vocab/1_dict.csv', index_col=0)
# print(len(seg1))
# segm1 = set(seg1.index)
# del seg1

# seg2 = pd.read_csv('segment_vocab/2_dict.csv', index_col=0)
# print(len(seg2))
# segm2 = set(seg2.index)
# del seg2

# seg3 = pd.read_csv('segment_vocab/63aafd6cb004f7d13370ef81_dict.csv', index_col=0)
# segm3 = set(seg3.index)
# del seg3


# print("========================================")
# slang12 = segm1 - segm2
# s1 = pd.Series(list(slang12), name='slang12').to_frame(name='token')
# print(s1.info())
# s1['word'] = s1['token'].apply(lambda x: token_to_word(x, as_dict=False))

# freq = []*len(s1)
# for row in s1.itertuples():
#     freq[row[0]] = merge_one_token_data(source_dict, row[1], datetime.today())['frequency']

# s1.to_csv('slang12.csv')
# print(slang12)

# print("========================================")
# slang23 = segm2 - segm3
# s2 = pd.Series(list(slang23), name='slang23').to_frame(name='token')
# print(s2.info())
# s2['word'] = s2['token'].apply(lambda x: token_to_word(x, as_dict=False))
# s2.to_csv('slang12.csv')
# print(slang23)


# print("========================================")
# slang32 = segm3 - segm2
# s3 = pd.Series(list(slang32), name='slang32').to_frame(name='token')
# print(s3.info())
# s3['word'] = s3['token'].apply(lambda x: token_to_word(x, as_dict=False))
# s3.to_csv('slang12.csv')
# print(slang32)


def get_unique_vocab(name1, name2):
    seg1 = pd.read_csv(f'storage/segment_vocab/{name1}.csv', index_col=0)
    print(name1, len(seg1))
    print(seg1.head(5))
    segm1 = set(seg1.index)
    # del seg1
    
    seg2 = pd.read_csv(f'storage/segment_vocab/{name2}.csv', index_col=0)
    print(name2, len(seg2))
    print(seg2.head(5))
    segm2 = set(seg2.index)
    # del seg2
    
    
    print("========================================")
    slang12 = segm1 - segm2
    s1 = pd.Series(list(slang12), name='slang12').to_frame(name='token')
    print(s1.head(5))
    print(s1.info())
    s1['word'] = s1['token'].apply(lambda x: token_to_word(x, as_dict=False))
    s1.join(seg1, how='left')
    s1.sort_values(by=['sum_count', 'growth'])
    print(s1.info())
    # freq = []*len(s1)
    # for row in s1.itertuples():
    #     freq[row[0]] = merge_one_token_data(source_dict, row[1], datetime.today())['frequency']
    s1.to_csv(f'storage/unique/{name1}__{name2}.csv')
    print(slang12)
    del s1
    del slang12
    
    
    print("========================================")
    slang21 = segm2 - segm1
    s2 = pd.Series(list(slang21), name='slang21').to_frame(name='token')
    s2['word'] = s2['token'].apply(lambda x: token_to_word(x, as_dict=False))
    s2.join(seg2, how='left')
    s2.sort_values(by=['sum_count', 'growth'])
    print(s2.info())
    # freq = []*len(s2)
    # for row in s2.itertuples():
    #     freq[row[0]] = merge_one_token_data(source_dict, row[1], datetime.today())['frequency']
    s2.to_csv(f'storage/unique/{name2}__{name1}.csv')
    print(slang21)
    
    
    
def all_slangs():
    vocab_file_list = os.listdir('storage/segment_vocab')
    try:
        vocab_file_list.remove('.gitkeep')
    except ValueError:
        print('no file named .gitkeep found')
    print(vocab_file_list)
    pairs = combinations(vocab_file_list, 2)
    for pair in pairs:
        get_unique_vocab(pair[0][:-4], pair[1][:-4])

all_slangs()