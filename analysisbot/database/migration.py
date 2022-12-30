from pymongo.mongo_client import MongoClient
from analysisbot.logging.logger import _logger

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client['trends_analysis']
    
    #! drop all
    # client.drop_database('trends_analysis')
    
    
    #! drop collection
    # client.trends_analysis.drop_collection('processed_data')
    client.trends_analysis.processed_data.delete_many({"type": "vk"})
    # client.trends_analysis.drop_collection('users')
        
    #! show entire database['dictionary'] in file dict.txt
    # dic = db['dictionary'].find({})
    # res = [str(r)+'\n' for r in dic]
    # with open('dict.txt', 'w', encoding='utf-8') as f:
    #     f.writelines(res)
    
    # print(db.dictionary.count_documents({}))
    # client.close()

    _logger.warning('database [trends_analysis] cleared')