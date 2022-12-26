from pymongo.mongo_client import MongoClient
import os

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client['trends_analysis']
    
    #! drop all
    client.drop_database('trends_analysis')
    print('database [trends_analysis] cleared')
    os.remove('storage/ref.csv')