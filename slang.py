import pandas as pd
from analysisbot.database.mongodb import MongoManager


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
        
mongodb = MongoManager.get_instance()
seg1 = pd.read_csv('1_dict.csv', index_col=0)
print(len(seg1))
segm1 = set(seg1.index)
del seg1

seg2 = pd.read_csv('2_dict.csv', index_col=0)
print(len(seg2))
segm2 = set(seg2.index)
del seg2

seg3 = pd.read_csv('63aafd6cb004f7d13370ef81_dict.csv', index_col=0)
segm3 = set(seg3.index)
del seg3


print("========================================")
slang12 = segm1 - segm2
s1 = pd.Series(list(slang12), name='slang12').to_frame(name='token')
print(s1.info())
s1['word'] = s1['token'].apply(lambda x: token_to_word(x, as_dict=False))
s1.to_csv('slang12.csv')
print(slang12)

print("========================================")
slang23 = segm2 - segm3
pd.Series(list(slang23), name='slang23').to_csv('slang23.csv')
print(slang23)


print("========================================")
slang32 = segm3 - segm2
pd.Series(list(slang32), name='slang32').to_csv('slang32.csv')
print(slang32)
