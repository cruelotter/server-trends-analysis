from datetime import time, timedelta, datetime
from dateutil.relativedelta import relativedelta


ACCEESS_DENIED = '''Доступ запрещен. Пользователь {} не найден в списке допуска.'''
ACCEESS_GRANTED = '''Доступ разрешен'''

TXT_START = '''
Добро пожаловать, {}! Это бот для анализа трендов в медиа-ресурсов.

Бот обрабатывает посты из медиа-источников за определенный период и выделяет тренды за последнее время.
В результате вы получите с топ трендов и файл-отчет.
Процесс сбора и обработки данных может занять какое-то время, пожалуйста, проявите терпение.

При возникновении проблем, пожалуйста, свяжитесь с @cruelotter
'''

TXT_HELP = '''
Настройки профиля:
\t/set_sources - Изменить список источников
\t/set_history - Изменить период, за который считать статистику
\t/set_trend - Изменить период расчета трендов
\t/set_schedule - Время автоматической рассылки
Доступные команды:
\t/help - Помощь
\t/start - Перезапустить бота
\t/get_trends - Расчитать тренды трендов
\t/profile - Показать текущие настройки

При возникновении проблем, пожалуйста, свяжитесь с @cruelotter
'''

TXT_SETTINGS = '''
Настройки
'''

TXT_SOURCES = '''Введите список источников в формате ссылок, каждая ссылка с новой строки.
Доступны телеграм-каналы, группы ВК, потоки в Тинькофф Журнал
Нажмите /cancel для отмены действия.'''

DEFAULT_SOURCES =['t.me/FinZoZhExpert', 't.me/investorbiz', 't.me/Reddit',
                  't.me/tinkoff_invest_official', 't.me/coinkeeper', 't.me/vcnews',
                  'vk.com/nrnews24', 'vk.com/noboring_finance',
                  'https://journal.tinkoff.ru/flows/business-russia/', 'https://journal.tinkoff.ru/flows/crisis/',
                  'https://journal.tinkoff.ru/flows/edu-news/', 'https://journal.tinkoff.ru/flows/opinion/', 'https://journal.tinkoff.ru/flows/hobby/']
    # 'https://journal.tinkoff.ru/flows/business-opinion/',
    # 'https://journal.tinkoff.ru/flows/opinion/',]
    # 'https://journal.tinkoff.ru/flows/podrabotka/',
    # 'https://journal.tinkoff.ru/flows/edu-news/',
    # 'https://journal.tinkoff.ru/flows/business-opinion/',
    # 'https://journal.tinkoff.ru/flows/opinion/',]

TXT_HISTORY = '''Выберите, за какой период использовать историю.
Нажмите /default для выбора значения по умолчанию.
Нажмите /cancel для отмены действия.'''

DEFAULT_HISTORY: int = 4
OPTIONS_HISTORY = [['6 месяцев', '1 год'],
                   ['2 года', '3 года'],
                   ['/default', '/cancel']]

OPTION_VALUE_HISTORY = {'6 месяцев': 6, 
                '1 год': 12,
                '2 года': 12*2,
                '3 года': 12*3}


TXT_TREND = '''Выберите, за какой интервал определять тренды.
Нажмите /default для выбора значения по умолчанию.
Нажмите /cancel для отмены действия.'''

DEFAULT_TREND: int = 14

OPTIONS_TREND = [['За 1 месяц'],
                 ['За 1 неделю','За 2 недели'],
                 ['/default', '/cancel']]

OPTION_VALUE_TREND = {'За 1 неделю': 7,
              'За 2 недели': 14,
              'За 1 месяц': 30}


TXT_SCHEDULE_DAYS = '''Выберите, как часто получать автоматическую рассылку.
Нажмите /default для выбора значения по умолчанию.
Нажмите /cancel для отмены действия.'''

DEFAULT_SCHEDULE_DAYS = [1,3,5]

OPTIONS_SCHEDULE_DAYS = [['По будним дням', 'Никогда'],
                         ['Пн', 'Пн Ср Пт'],
                         ['/default', '/cancel']]

OPTION_VALUE_SCHEDULE = {'По будним дням': [1,2,3,4,5],
                 'Пн': [1],
                 'Пн Ср Пт': [1,3,5],
                 'Никогда': []}


TXT_SCHEDULE_TIME = '''Введите время автоматического запуска бота в формате чч:мм
Нажмите /default для выбора значения по умолчанию.
Нажмите /cancel для отмены действия.'''

DEFAULT_SCHEDULE_TIME = time(hour=10, minute=0)


PROFILE = '''
Ваши текущие настройки:
id: {},
История за {} месяца(ев),
Выделять тренд за {} дня(ей),
Автоматическая рассылка по {} в {},
Источники: {}
'''

ERROR = 'Извинтите, произошла ошибка.'

STATUS_TYPES = {
0: 'В данный момент ничего не обрабатывается',
1: 'В данный момент происходит парсинг данных. Это может занять некоторое время',
2: 'В данный момент мы вычисляем тренды. Это может занять некоторое время',
3: 'Произошла ошибка'}


MAIN_KEYBOARD = [['Выбрать сегмент'],
                 ['Расчитать тренды'],
                 ['Профиль'],
                 ['Изменить настройки']]