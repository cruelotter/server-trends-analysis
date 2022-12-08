import pandas as pd
from myapp.logging.logger import _logger

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

AGE_SEGMENTS = {
    "Подростки" : (14, 18),
    "Молодежь" : (18, 25),
    "25-40 лет" : (25, 40),
    "40 лет и старше" : (40, 60),
    "Все": (18, 60)
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


def filter_sources(age, gender, geo):
    try:
        sources = pd.read_csv('sources.csv', index_col=0)
        if gender != 'ALL':
            sources.drop(sources[sources['gender']!=gender].index, inplace=True)
        if geo != 'ALL':
            sources.drop(sources[sources['geo']!=geo].index, inplace=True)
        sources['age_filter'] = sources['age'].apply(lambda x: bool(str(age) in x))
        sources.drop(sources[sources['age_filter']==False].index, inplace=True)
        return sources['name'].tolist()
    
    except Exception as e:
        _logger.error(e)