from datetime import time, timedelta, datetime
from dateutil.relativedelta import relativedelta


ACCEESS_DENIED = '''Доступ запрещен. Пользователь {} не найден в списке допуска.'''
ACCEESS_GRANTED = '''Доступ разрешен'''

TXT_START = '''
Добро пожаловать, {}! Это бот для анализа трендов в медиа-ресурсов.

Бот обрабатывает посты из медиа-источников за определенный период и выделяет тренды за последнее время (срок устанавливается).
В результате вы получите файл с топом трендов и графиками поведения каждого топика за всю установленную историю.
Процесс сбора и обработки данных может занять какое-то время, пожалуйста, проявите терпение.
'''

TXT_HELP = '''
Настройки профиля:
\t/set_sources - Изменить список источников
\t/set_history - Изменить период, за который считать статистику
\t/set_trend - Изменить период расчета трендов
\t/set_schedule - Время автоматической рассылки
Доступные команды:
\t/help - Помощь
\t/get_trends - Начать расчет трендов
\t/profile - Показать текущие настройки
\t/start - Перезапустить бота и удалить текущий профиль

При возникновении проблем, пожалуйста, свяжитесь с @cruelotter
'''

TXT_SOURCES = '''Введите список источников в формате ссылок, каждая ссылка с новой строки.
Доступны телеграм-каналы, группы ВК, потоки в Тинькофф Журнал
Нажмите /default для выбора значения по умолчанию.
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
DEFAULT_HISTORY: int = 2
OPTIONS_HISTORY = [['6 месяцев', '1 год'],
                   ['3 года', '5 лет']]

TXT_TREND = '''Выберите, за какой интервал определять тренды.
Нажмите /default для выбора значения по умолчанию.
Нажмите /cancel для отмены действия.'''
DEFAULT_TREND: int = 7
OPTIONS_TREND = [['За 2 дня', 'За 1 неделю'],
                 ['За 2 недели', 'За 1 месяц']]

TXT_SCHEDULE_DAYS = '''Выберите, как часто получать автоматическую рассылку.
Нажмите /default для выбора значения по умолчанию.
Нажмите /cancel для отмены действия.'''
DEFAULT_SCHEDULE_DAYS = [1,4]
OPTIONS_SCHEDULE_DAYS = [['Каждый день', 'Пн Ср Пт'],
                         ['Пн', 'Никогда']]

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