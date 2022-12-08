from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from time import sleep
from myapp.bot.constants import *
from myapp.bot.user import UserManager
from myapp.bot.conversations import *
from myapp.logging.logger import _logger

HISTORY, TREND, SCHEDULE_D, SCHEDULE_T = range(4)


def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_GRANTED
        )
    sleep(2)
    username = update.effective_user.full_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TXT_START.format(username)
    )
    sleep(2)
    # reply_keyboard = [['/default', '/cancel']]
    reply_keyboard = OPTIONS_HISTORY
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_HISTORY,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 2 года", resize_keyboard=True
        ),
    )
    return HISTORY


async def set_custom_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "1 год":
        history = 12*1
    elif update.message.text == "3 года":
        history = 12*3
    elif update.message.text == "6 месяцев":
        history = 6
    elif update.message.text =="5 лет":
        history = 12*5
    else:
        await update.message.reply_text(
            "Ошибка, такой вариант не предусмотрен",
            reply_markup=ReplyKeyboardRemove()
        )
        return HISTORY
    UserManager.set_history_duration(update.effective_chat.id, history)
    reply_keyboard = OPTIONS_TREND
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_TREND,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 7 дней"
        ),
    )
    return TREND
        
    
async def set_default_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    UserManager.set_history_duration(update.effective_chat.id, DEFAULT_HISTORY)
    reply_keyboard = OPTIONS_TREND
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_TREND,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 7 дней"
        ),
    )
    return TREND


async def set_custom_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "За 1 месяц":
        trend = 30
    elif update.message.text == "За 2 недели":
        trend = 14
    elif update.message.text == "За 1 неделю":
        trend = 7
    elif update.message.text == "За 2 дня":
        trend = 2
    UserManager.set_trend_period(update.effective_chat.id, trend)
    reply_keyboard = OPTIONS_SCHEDULE_DAYS
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_SCHEDULE_DAYS,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: Раз в 3 дня"
        ),
    )
    return SCHEDULE_D
        
    
async def set_default_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    UserManager.set_trend_period(update.effective_chat.id, DEFAULT_TREND)
    reply_keyboard = OPTIONS_SCHEDULE_DAYS
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_SCHEDULE_DAYS,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: Раз в 3 дня"
        ),
    )
    return SCHEDULE_D
    
    
async def set_custom_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Каждый день":
        days = [1,2,3,4,5]
    elif update.message.text == "Пн Ср Пт":
        days = [1,3,5]
    elif update.message.text == "Пн":
        days = [1]
    elif update.message.text == "Никогда":
        days = []
    UserManager.set_schedule_days(update.effective_chat.id, days)
    reply_keyboard = [['/default', '/cancel']]
    await update.message.reply_text(
        TXT_SCHEDULE_TIME,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 10:00", resize_keyboard=True
        ),
    )
    return SCHEDULE_T
        
    
async def set_default_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    UserManager.set_schedule_days(update.effective_chat.id, DEFAULT_SCHEDULE_DAYS)
    reply_keyboard = [['/default', '/cancel']]
    await update.message.reply_text(
        TXT_SCHEDULE_TIME,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 10:00", resize_keyboard=True
        ),
    )
    return SCHEDULE_T


async def set_custom_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    input = update.message.text
    input = input.split(':')

    if input[0].isdecimal() and input[1].isdecimal():
        schedule_time = time(hour=int(input[0]), minute=int(input[1]))
        UserManager.set_schedule_time(chat_id, schedule_time)
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()
            
    usr = UserManager.get_from_db(chat_id)
    sd = usr.schedule_days
    if not sd == "":
        days = sd.split()
        t_days = tuple([int(d) for d in days])
        print(t_days)
        context.job_queue.run_daily(get_trends_manager, chat_id=chat_id, name=str(chat_id), time=time().fromisoformat(usr.schedule_time), days=t_days)
    await update.message.reply_text(
        f"Настройка профиля завершена",
        reply_markup=ReplyKeyboardMarkup(
            [['Выбрать сегмент']], resize_keyboard=True
        )
    )
    return ConversationHandler.END


async def set_default_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    usr = UserManager.get_from_db(chat_id)
    UserManager.set_schedule_time(chat_id, DEFAULT_SCHEDULE_TIME)
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()
    
    sd = usr.schedule_days
    if not sd == "":
        days = sd.split()
        t_days = tuple([int(d) for d in days])
        context.job_queue.run_daily(get_trends_manager, chat_id=chat_id, name=str(chat_id), time=time().fromisoformat(usr.schedule_time), days=t_days)
    await update.message.reply_text(
        f"Настройка профиля завершена",
        reply_markup=ReplyKeyboardMarkup(
            [['Выбрать сегмент']], resize_keyboard=True
        )
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выход из настроек профиля",
        reply_markup=ReplyKeyboardMarkup(
            [['Выбрать сегмент']], resize_keyboard=True
        )
    )
    return ConversationHandler.END


conversation_start = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            HISTORY: [
                CommandHandler("default", set_default_2),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom_2),
            ],
            TREND: [
                CommandHandler("default", set_default_3),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom_3),
            ],
            SCHEDULE_D: [
                CommandHandler("default", set_default_4),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom_4),
            ],
            SCHEDULE_T: [
                CommandHandler("default", set_default_5),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom_5),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
