from pymongo.mongo_client import MongoClient
from myapp.logging.logger import _logger

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    print("Avalible collections: 1) dictionary 2) processed_data 3) users")
    collection = input()
    db = client['trends_analysis']
    dic = db[collection].find({})
    res = [str(r)+'\n' for r in dic]
    with open(f'db_{collection}.txt', 'w', encoding='utf-8') as f:
        f.writelines(res)
    
    c = db[collection].count_documents({})
    client.close()

    _logger.warning(f'table [dictionary] {c} docs saves to db.txt')