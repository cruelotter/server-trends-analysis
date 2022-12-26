from datetime import time
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from analysisbot.bot.constants import *
from analysisbot.bot.user import User, UserManager
from analysisbot.logging.logger import _logger
from analysisbot.model import *
from analysisbot.bot.conversations.get_trends_manager import get_trends_manager


def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

DAYS, TIME = range(2)

async def set_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    reply_keyboard = OPTIONS_SCHEDULE_DAYS
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_SCHEDULE_DAYS,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: Раз в 3 дня"
        ),
    )
    return DAYS


async def set_custom_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Каждый день":
        days = [1,2,3,4,5]
    elif update.message.text == "Пн Ср Пт":
        days = [1,3,5]
    elif update.message.text == "Пн":
        days = [1]
    elif update.message.text == "Никогда":
        days = []
    # usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_schedule_days(update.effective_chat.id, days)

    reply_keyboard = [['/default', '/cancel']]
    await update.message.reply_text(
        TXT_SCHEDULE_TIME,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 10:00", resize_keyboard=True
        ),
    )
    return TIME
        
    
async def set_default_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_schedule_days(update.effective_chat.id, DEFAULT_SCHEDULE_DAYS)

    reply_keyboard = [['/default', '/cancel']]
    await update.message.reply_text(
        TXT_SCHEDULE_TIME,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 10:00", resize_keyboard=True
        ),
    )
    return TIME


async def set_custom_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        context.job_queue.run_daily(get_trends_manager, chat_id=chat_id, name=str(chat_id), time=time().fromisoformat(usr.schedule_time), days=t_days)
    # context.job_queue.run_repeating(get_trends_manager, chat_id=chat_id, name=str(chat_id), interval=usr.schedule_days, first=(usr.first_job+usr.schedule_time))
        await update.message.reply_text(
            f"Автоматическая рассылка включена",
            reply_markup=ReplyKeyboardMarkup(
                [['/get_trends']], resize_keyboard=True
            )
        )
    else:
        await update.message.reply_text(
            f"Автоматическая рассылка выключена",
            reply_markup=ReplyKeyboardMarkup(
                [['/get_trends']], resize_keyboard=True
            )
        )
    return ConversationHandler.END


async def set_default_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    UserManager.set_schedule_time(chat_id, DEFAULT_SCHEDULE_TIME)
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()
    usr = UserManager.get_from_db(chat_id)
    sd = usr.schedule_days
    if not sd == "":
        days = sd.split()
        t_days = tuple([int(d) for d in days])
    
        context.job_queue.run_daily(get_trends_manager, chat_id=chat_id, name=str(chat_id), time=time().fromisoformat(usr.schedule_time), days=t_days)
        await update.message.reply_text(
            f"Автоматическая рассылка включена",
            reply_markup=ReplyKeyboardMarkup(
                [['/get_trends']], resize_keyboard=True
            )
        )
    else:
        await update.message.reply_text(
            f"Автоматическая рассылка выключена",
            reply_markup=ReplyKeyboardMarkup(
                [['/get_trends']], resize_keyboard=True
            )
        )
    # context.job_queue.run_repeating(get_trends_manager, chat_id=chat_id, name=str(chat_id), interval=usr.schedule_days, first=(usr.first_job+usr.schedule_time))
    return ConversationHandler.END

    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Не внесено изменений",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
    

conversation_schedule = ConversationHandler(
        entry_points=[CommandHandler("set_schedule", set_schedule)],
        states={
            DAYS: [
                CommandHandler("default", set_default_days),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom_days),
            ],
            TIME: [
                CommandHandler("default", set_default_time),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom_time),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
