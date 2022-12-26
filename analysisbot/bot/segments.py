import pandas as pd
import json

from analysisbot.database.mongodb import MongoManager
from analysisbot.bot.user import Filters
from analysisbot.bot.constants import *
from analysisbot.logging.logger import _logger


BUSINESS = [
't.me/FinZoZhExpert',
't.me/investorbiz', 
't.me/tinkoff_invest_official', 
't.me/coinkeeper',
't.me/TochkaUP',
't.me/BizLike',
'vk.com/noboring_finance',
'https://journal.tinkoff.ru/flows/business-russia/',
'https://journal.tinkoff.ru/flows/crisis/',
'https://journal.tinkoff.ru/flows/business-opinion/',
'https://journal.tinkoff.ru/flows/goskontrol/'
]

TOPIC_SEGMENTS = {
    "Бизнес": "BUSINESS",
    "Общие": "ALL"
}

TYPE_OF_CHOICE = {
    "Выбрать из пресетов":0,
    "Создать свой сегмент":1,
    "Выбрать по фильтрам":2
}

AGE_SEGMENTS = {
    "Подростки" : ["-18"],
    "Молодежь" : ["18-21", "21-24"],
    "25-35 лет" : ["24-27", "27-30", "30-35"],
    "35-45" : ["35-45"],
    "45 лет и старше" : ["45+"],
    "Все": 'ALL'
}

GENDER_SEGMENTS = {
    "Женщины": "F",
    "Мужчины" : "M",
    "Все" : "ALL"
}

GEO_SEGMENTS = {
    "Вся Россия" : "ALL",
    "Москва" : "MSK",
    "Санкт-Петербург" : "SPB",
    "Дальний Восток" : "EAST",
    "Юг": "SOUTH",
    "Сибирь" : "SIB",
    "Северо-Запад" : "NW"
}

        
class Segment:
    
    EQUEL_AGES = {
        '-18': 12.5,
        '18-21': 12.5,
        '21-24': 12.5,
        '24-27': 12.5,
        '27-30': 12.5,
        '30-35': 12.5,
        '35-45': 12.5,
        '45+': 12.5,
    }
    
    def __init__(self, user_id, name='Безымянный', source_list=[]) -> None:
        self.user_id = id
        self.name = name
        self.source_list = source_list
        
        
    def to_dict(self):
        return {'user_id': self.user_id,
                'name': self.name,
                'source_list': self.source_list}

class SegmentManager:
    BaseSegmentList = [
        {'name':"Молодежь Москва",
         'source_list':""},
        
        {'name':"Дети до 18 лет",
         'source_list':""},
        
        {'name':"Домохозяйки 30-45",
         'source_list':""},
        
        {'name':"Родители Санкт-Петербург",
         'source_list':""},
        
        {'name':"Рабочий класс 35-50 Сибирь",
         'source_list':""},
        
        {'name':"Молодая семья 20-30 Северо-Запад",
         'source_list':""},
        
        {'name':"Молодежь Дальний Восток",
         'source_list':""},
    ]
        
    @staticmethod
    def exist(id, name):
        found = MongoManager.find_data(
            'segments',
            {'user_id': id,
             'name': name}
            )
        if found is None:
            found = Segment(id, name)
            MongoManager.insert_data('segments', found.to_dict())
            return False
        else:
            return True
        
        
    @staticmethod
    def check_base(id):
        for base in SegmentManager.BaseSegmentList:
            MongoManager.update_data(
                'segments',
                {'user_id': id,
                 'name': base['name'],
                 'source_list': base['source_list']
                 },
                {'source_list': base['source_list']}
            )
    
    
    @staticmethod
    def age_filter(s: str, prefered):
        s = s.replace(";", ",")
        dict_age = json.loads(s)
        # _logger.info(dict_age)
        sum = 0
        for category in prefered:
            sum += dict_age[category]
        if sum >= 25:
            return True
        else:
            return False
        
    
    @staticmethod   
    def get_filtered_sources(age, gender, geo):
        _logger.info(f"get_filter_sources args: {age}, {gender}, {geo}")
        # try:
        sources = pd.read_csv('./analysisbot/bot/sources.csv', index_col=0)
        # sources = sources.convert_dtypes()
        # print(sources.to_string())
        try:
            if gender != 'ALL':
                if gender=='M':
                    sources.drop(sources[(sources['male']<50)].index, inplace=True)
                    # print('male del')
                elif gender=='F':
                    sources.drop(sources[(sources['female']<50)].index, inplace=True)
            if geo != 'ALL':
                sources.drop(sources[(sources['geo']!=geo) & (sources['geo']!='ALL')].index, inplace=True)
            if age != 'ALL':
                sources['age_filter'] = sources['age_pct'].apply(lambda x: SegmentManager.age_filter(x, age))
                sources.drop(sources[sources['age_filter']==False].index, inplace=True)
            
            lst = sources['name'].tolist()
            if len(lst)==0 or lst is None:
                _logger.error("No sources found")
                return 1, []
            else:
                return 1, lst
        
        except Exception as e:
            _logger.error("there is an error in filters")
            _logger.error(e)
    
    
    @staticmethod
    def get_preset_sources(id, name):  
        found = MongoManager.find_data(
            'segments',
            {'user_id': id,
             'name': name}
            )
        return found['_id'], found['source_list']

    
    @staticmethod
    def set_sources_custom(id, name, source_list):
        MongoManager.update_data(
            'segments',
            {'user_id': id,
             'name': name},
            {'source_list': source_list}
        )
        found = MongoManager.find_data('segments', {'user_id': id, 'name': name})
        return found[-1]
        
    
    @staticmethod
    def get_user_segments(id):
        found = MongoManager.find_data(
            'segments',
            {'user_id': id}
        )
        return found
        
    
    # @staticmethod
    # def set_sources_filtered(id):
    #     filters = Filters.get_filters()
    #     source_list = SegmentManager.filter_sources(filters.age, filters.gender, filters.geo)
    #     source_list = " ".join(source_list)
    #     SegmentManager.set_sources_custom(id, name, source_list)
     