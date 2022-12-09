import pymongo
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient


class MongoManager:
    
    __instance = None
    __client = None
    
    @staticmethod 
    def get_instance():
        if MongoManager.__instance == None:
            MongoManager()
        return MongoManager.__instance
     
    def __init__(self):
        if MongoManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MongoManager.__client = MongoClient('localhost', 27017)
            MongoManager.__instance = Database(client=MongoManager.__client, name='trends_analysis')
    
    @staticmethod      
    def insert_data(collection_name: str, data):
        collection = MongoManager.__instance[collection_name]
        return collection.insert_one(data).inserted_id

    @staticmethod
    def find_data(collection_name, elements, multiple=False):
        collection = MongoManager.__instance[collection_name]
        if multiple:
            results = collection.find(elements, limit=10).limit(10)
            return [r for r in results]
        else:
            return collection.find_one(elements)
        
    @staticmethod
    def find_random(collection_name, elements):
        collection = MongoManager.__instance[collection_name]
        collection.aggregate([
            {'$match': elements},
            {'$sample': {'size': 3}}
        ])
    
    @staticmethod
    def update_data(collection_name: str, query_element, new_value):
        collection = MongoManager.__instance[collection_name]
        collection.update_one(query_element, {'$set': new_value}, upsert=True)
    
    @staticmethod   
    def count(collection_name: str):
        collection = MongoManager.__instance[collection_name]
        return collection.count_documents({})
    


# class MongoDB():
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, 'instance') or not cls.instance:
#           cls.instance = super().__new__(cls)
#         return cls.instance

#     def __init__(self) -> None:
#         self.client = MongoClient('localhost', 27017)
#         self.db = self.client['TrendAnalysisDB']
#         self.collections = {
#             'dictionary': self.db['dictionary'],
#             'users': self.db['users'],
#             'processed_data': self.db['processed_data']
#         }
#         # self.dictionary_collection = self.db['dictionary']
#         # self.users_collection = self.db['users']
#         # self.processed_data_collection = self.db['processed_data']
        
    
#     def insert_data(self, name: str, data):
#         return self.collections[name].insert_one(data).inserted_id

    
#     def find_data(self, name, elements, multiple=False):
#         if multiple:
#             results = self.collections[name].find(elements)
#             return [r for r in results]
#         else:
#             return self.collections[name].find_one(elements)

    
#     def update_data(self, name: str, query_element, new_value):
#         self.collections[name].update_one(query_element, {'$set': new_value}, upsert=True)
        
#     def count(self, name: str):
#         return self.collections[name].count_documents({})