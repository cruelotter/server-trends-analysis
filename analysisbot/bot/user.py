import json
import pandas as pd
from datetime import datetime, time
# from dateutil.relativedelta import relativedelta

from analysisbot.database.mongodb import MongoManager
from analysisbot.bot.constants import *
from analysisbot.logging.logger import _logger


class Filters:
    def __init__(self, id, topic='ALL', age=(18, 60), gender='ALL', geo='ALL') -> None:
        found: dict = MongoManager.find_data(
            'filters',
            {'_id': id}
        )
        if found is None:
            self.id = id
            self.topic = topic
            self.age = age
            self.gender = gender
            self.geo = geo
        else:
            self.id = id
            self.topic = found['topic']
            self.age = found['age']
            self.gender = found['gender']
            self.geo = found['geo']
    
    
    @staticmethod      
    def from_dict(dict):
        return Filters(dict['id'], dict['topic'],
                       dict['age'], dict['gender'],
                       dict['geo'])
    
    @staticmethod
    def to_dict(self):
        return {
        'id': self.id,
        'topic':self.topic,
        'age':self.age,
        'gender':self.gender,
        'geo':self.geo}
    
    
    @staticmethod
    def check_exists(id):
        found: dict = MongoManager.find_data(
            'filters',
            {'_id': id}
        )
        if found is None:
            user = Filters(id)
            MongoManager.insert_data(
                'filters',
                user.to_dict()
            )
            _logger.info(found if found is not None else f"User not found. Creating new...{json.dumps(user.to_dict(), indent=2)}")
    
       
    @staticmethod
    def set_topic(id, topic):
        Filters.check_exists(id)
        MongoManager.update_data(
            'filters',
            {'_id': id},
            {'topic': topic})
    
    @staticmethod
    def set_age(id, age):
        Filters.check_exists(id)
        MongoManager.update_data(
            'filters',
            {'_id': id},
            {'age': age})
        _logger.info('Age filter updated')
    
       
    @staticmethod
    def set_gender(id, gender):
        Filters.check_exists(id)
        MongoManager.update_data(
            'filters',
            {'_id': id},
            {'gender': gender})
        
    @staticmethod
    def set_geo(id, geo):
        Filters.check_exists(id)
        MongoManager.update_data(
            'filters',
            {'_id': id},
            {'geo': geo})
        
    @staticmethod
    def get_filters(id):
        found = MongoManager.find_data('filters',{'_id': id})
        return Filters.from_dict(found)

class User:
    def __init__(self, id, sources=DEFAULT_SOURCES, history: int=DEFAULT_HISTORY,
                 trend: int=DEFAULT_TREND, schedule_days=DEFAULT_SCHEDULE_DAYS, 
                 schedule_time=DEFAULT_SCHEDULE_TIME.isoformat(),
                 status=0) -> None:
        self.id: int = id
        self.status: int = status
        self.history_duration: int = history
        self.trend_period: int = trend
        if schedule_days == []:
            self.schedule_days = ""
        else:
            s = [str(x) for x in schedule_days]
            self.schedule_days= " ".join(s)
        self.schedule_time: str = schedule_time
        if type(sources)==list:
            long_str = ''
            for s in sources:
                long_str+= s
                long_str+=' '
        else: long_str = sources
        self.sources: str = long_str
    
    def to_dict(self) -> dict:
        return {
            '_id': self.id,
            'sources': self.sources,
            'history_duration': self.history_duration,
            'trend_period': self.trend_period,
            'schedule_days': self.schedule_days,
            'schedule_time': self.schedule_time,
            'status': self.status
            }
        
    # def from_dict(self, dict): 
    #     self.id = dict['_id']
    #     self.status = dict['status']
    #     self.history_duration = dict['history_duration']
    #     self.trend_period = dict['trend_period']
    #     self.schedule_days = dict['schedule_days']
    #     self.schedule_time = dict['schedule_time']
    #     self.first_job = dict['first_job']
    #     self.sources = dict['sources']

class UserManager:
    
    db = MongoManager.get_instance()
    
    @staticmethod
    def get_from_db(id):
        found: dict = MongoManager.find_data(
            'users',
            {'_id': id}
        )
        if found is None:
            user = User(id)
            MongoManager.insert_data(
                'users',
                user.to_dict()
            )
            _logger.info(found if found is not None else f"User not found. Creating new...{json.dumps(user.to_dict(), indent=2)}")
        else:
            user = User(*found.values())
            print(found)
            _logger.info(f"User...{json.dumps(user.to_dict(), indent=2)}")
        _logger.warning(user.to_dict())
        return user
    
    @staticmethod
    def check_exists(id):
        found: dict = MongoManager.find_data(
            'users',
            {'_id': id}
        )
        if found is None:
            user = User(id)
            MongoManager.insert_data(
                'users',
                user.to_dict()
            )
            _logger.info(found if found is not None else f"User not found. Creating new...{json.dumps(user.to_dict(), indent=2)}")
        
    
    @staticmethod
    def set_status(id, status):
        UserManager.check_exists(id)
        MongoManager.update_data(
            'users',
            {'_id': id},
            {'status': status})
    
    @staticmethod    
    def set_history_duration(id, history_duration):
        UserManager.check_exists(id)
        MongoManager.update_data(
            'users',
            {'_id': id},
            {'history_duration': history_duration})
     
    @staticmethod   
    def set_trend_period(id, trend_period):
        UserManager.check_exists(id)
        MongoManager.update_data(
            'users',
            {'_id': id},
            {'trend_period': trend_period})
    
    @staticmethod   
    def set_schedule_days(id, schedule_days: tuple):
        UserManager.check_exists(id)
        s = [str(x) for x in schedule_days]
        s_schedule_days= " ".join(s)
        MongoManager.update_data(
            'users',
            {'_id': id},
            {'schedule_days': s_schedule_days})
    
    @staticmethod  
    def set_schedule_time(id, schedule_time: time):
        UserManager.check_exists(id)
        MongoManager.update_data(
            'users',
            {'_id': id},
            {'schedule_time': schedule_time.isoformat()})
        
    @staticmethod   
    def set_sources(id, sources):
        UserManager.check_exists(id)
        long_str = ''
        for s in sources:
            long_str+= s
            long_str+=' '
        MongoManager.update_data(
            'users',
            {'_id': id},
            {'sources': long_str})
       
    @staticmethod
    def get_all():
        UserManager.check_exists(id)
        return MongoManager.find_data('users', {}, multiple=True)
        
    
        
      
    # def set_schedule_days(self, days: int) -> None:
    #     self.schedule_days = timedelta(days=days)
        
        
    # def set_schedule_time(self, hours: int, minutes: int) -> None:
    #     self.schedule_time = time(hour=hours, minute=minutes)
    #     self.first_job = datetime.today()
    
    
    # def get_status(self):
    #     return self.status
    
    # @staticmethod
    # def to_dict(self) -> dict:
    #     return {
    #         '_id': self.id,
    #         'status': self.status,
    #         'history_duration': self.history_duration,
    #         'trend_period': self.trend_period,
    #         'schedule_days': self.schedule_days,
    #         'schedule_time': self.schedule_time,
    #         'first_job': self.first_job,
    #         'sources': self.sources,
    #         }
    # @staticmethod
    # def from_dict(self, dict): 
    #     self.id = dict['_id']
    #     self.status = dict['status']
    #     self.history_duration = dict['history_duration']
    #     self.trend_period = dict['trend_period']
    #     self.schedule_days = dict['schedule_days']
    #     self.schedule_time = dict['schedule_time']
    #     self.first_job = dict['first_job']
    #     self.sources = dict['sources']
        
    # def to_dict_noid(self):
    #     return {
    #         'status': self.status,
    #         'history_duration': self.history_duration,
    #         'trend_period': self.trend_period,
    #         'schedule_days': self.schedule_days,
    #         'schedule_time': self.schedule_time,
    #         'first_job': self.first_job,
    #         'sources': self.sources,
    #         }
    
    # def get_from_db(self):
    #     all = pd.read_csv('user_db.csv', index_col=0)
    #     print(all.index)
    #     cur = all.loc[self.id]
    #     self.from_dict(cur.to_dict())
    #     # except:
    #     #     print('ERRRROOOOR')
    
    # def save_to_db(self):
    #     try:
    #         all = pd.read_csv('user_db.csv', index_col=0)
    #         # print('read')
    #         try:
    #             cur = all.loc[self.id]
    #             all.loc[self.id]=self.to_dict_noid()
    #         except:
    #             # print('not found')
    #             new = self.to_dict_noid()
    #             # print(new)
    #             all = pd.concat([all, pd.DataFrame(new, index=[self.id])], ignore_index=False)
    #         # print(all.to_string())
    #         all.to_csv('user_db.csv')
    #     except:
    #         new = self.to_dict_noid()
    #         # print(new)
    #         all = pd.DataFrame(new, index=[self.id])
    #         all.to_csv('user_db.csv')
    #         # print(all.to_string())

    
    # def get_from_db(self):
    #     usr_dict = self.db.find_data({'_id': self.id})
    #     if usr_dict is None:
    #         _logger.info(f"User[{self.id}] not found")
    #     else:
    #         self.from_dict(usr_dict)
    #         _logger.info(f"User[{self.id}] read from database")
        
        
    # def save_to_db(self):
    #     usr_dict: dict = self.to_dict()
    #     self.db.update_data({"_id": self.id}, usr_dict)
    #     _logger.info(f"User[{self.id}] saved to database")