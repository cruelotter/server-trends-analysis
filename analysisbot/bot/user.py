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
        update = MongoManager.update_data(
            'filters',
            {'_id': id},
            {'topic': topic})
        _logger.info(update)
    
    @staticmethod
    def set_age(id, age):
        Filters.check_exists(id)
        update = MongoManager.update_data(
            'filters',
            {'_id': id},
            {'age': age})
        _logger.info(update)
    
       
    @staticmethod
    def set_gender(id, gender):
        Filters.check_exists(id)
        update = MongoManager.update_data(
            'filters',
            {'_id': id},
            {'gender': gender})
        _logger.info(update)
        
    @staticmethod
    def set_geo(id, geo):
        Filters.check_exists(id)
        update = MongoManager.update_data(
            'filters',
            {'_id': id},
            {'geo': geo})
        _logger.info(update)
        
    @staticmethod
    def get_filters(id):
        found = MongoManager.find_data('filters',{'_id': id})
        return Filters.from_dict(found)

class User:
    def __init__(self, id, segment_id=-1, sources=DEFAULT_SOURCES, history: int=DEFAULT_HISTORY,
                 trend: int=DEFAULT_TREND, schedule_days=DEFAULT_SCHEDULE_DAYS, 
                 schedule_time=DEFAULT_SCHEDULE_TIME.isoformat(),
                 status=0) -> None:
        self.id: int = id
        self.segment_id = segment_id
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
            'segment_id': self.segment_id,
            'sources': self.sources,
            'history_duration': self.history_duration,
            'trend_period': self.trend_period,
            'schedule_days': self.schedule_days,
            'schedule_time': self.schedule_time,
            'status': self.status
            }
        
 

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
            _logger.info(f"User not found. Creating new...{json.dumps(user.to_dict(), indent=2)}")
        else:
            user = User(*found.values())
            _logger.info(f"User...{json.dumps(user.to_dict(), indent=2)}")
        return user
    
    @staticmethod
    def check_exists(id):
        found: dict = MongoManager.find_data(
            'users',
            {'_id': id}
        )
        if found is None:
            user = User(id)
            print(user)
            print(user.to_dict())
            MongoManager.insert_data(
                'users',
                user.to_dict()
            )
        _logger.info(found if found is not None else f"User not found. Creating new...{json.dumps(user.to_dict(), indent=2)}")
        
    
    @staticmethod
    def set_status(id, status):
        UserManager.check_exists(id)
        update = MongoManager.update_data(
            'users',
            {'_id': id},
            {'status': status})
        _logger.info(update)
    
    @staticmethod    
    def set_history_duration(id, history_duration):
        UserManager.check_exists(id)
        update = MongoManager.update_data(
            'users',
            {'_id': id},
            {'history_duration': history_duration})
        _logger.info(update)
     
    @staticmethod   
    def set_trend_period(id, trend_period):
        UserManager.check_exists(id)
        update = MongoManager.update_data(
            'users',
            {'_id': id},
            {'trend_period': trend_period})
        _logger.info(update)
    
    @staticmethod   
    def set_schedule_days(id, schedule_days: tuple):
        UserManager.check_exists(id)
        s = [str(x) for x in schedule_days]
        s_schedule_days= " ".join(s)
        update = MongoManager.update_data(
            'users',
            {'_id': id},
            {'schedule_days': s_schedule_days})
        _logger.info(update)
    
    @staticmethod  
    def set_schedule_time(id, schedule_time: time):
        UserManager.check_exists(id)
        update = MongoManager.update_data(
            'users',
            {'_id': id},
            {'schedule_time': schedule_time.isoformat()})
        _logger.info(update)
        
    @staticmethod   
    def set_sources(id, segment_id, sources):
        UserManager.check_exists(id)
        long_str = ''
        for s in sources:
            long_str+= s
            long_str+=' '
        update = MongoManager.update_data(
            'users',
            {'_id': id},
            {'segment_id':segment_id, 'sources': long_str})
        _logger.info(update)
       
    @staticmethod
    def get_all():
        UserManager.check_exists(id)
        return MongoManager.find_data('users', {}, multiple=True)
