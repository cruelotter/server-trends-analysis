from pymongo.mongo_client import MongoClient
from myapp.logging.logger import _logger
import os

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client['trends_analysis']
    
    #! drop all
    client.drop_database('trends_analysis')
    _logger.warning('database [trends_analysis] cleared')
    os.remove('storage/ref.csv')