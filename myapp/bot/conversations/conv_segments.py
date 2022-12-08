# from datetime import timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

from myapp.bot.constants import *
from myapp.bot.user import UserManager, Filters
from myapp.bot.segments import *
from myapp.bot.conversations.get_trends_manager import get_trends_manager


def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

TOPIC, AGE, GENDER, GEO, TRENDS = range(5)

async def select_segment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return ConversationHandler.END
    reply_keyboard = [[key] for key in TOPIC_SEGMENTS.keys()]
    await update.message.reply_text(
        text="Выберите, для какой сферы вы хотите получить тренды",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return TOPIC
        
    
async def set_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Бизнес":
        UserManager.set_sources(update.effective_chat.id, BUSINESS)
        return ConversationHandler.END
        
    Filters.set_topic(update.effective_chat.id, TOPIC_SEGMENTS[update.message.text])
    
    await update.message.reply_text(
        "Выберите возраст целевой аудитории",
        reply_markup=ReplyKeyboardMarkup(
            [[key] for key in AGE_SEGMENTS.keys()], resize_keyboard=True
        )
    )
    return AGE


async def set_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    Filters.set_age(update.effective_chat.id, AGE_SEGMENTS[update.message.text])
    
    await update.message.reply_text(
        "Выберите пол целевой аудитории",
        reply_markup=ReplyKeyboardMarkup(
            [[key] for key in GENDER_SEGMENTS.keys()], resize_keyboard=True
        )
    )
    return GENDER
   
    
async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Filters.set_gender(update.effective_chat.id, AGE_SEGMENTS[update.message.text])
    await update.message.reply_text(
        "Выберите регион целевой аудитории",
        reply_markup=ReplyKeyboardMarkup(
            [[key] for key in GEO_SEGMENTS.keys()], resize_keyboard=True
        )
    )
    return GEO

   
async def set_geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Filters.set_geo(update.effective_chat.id, GEO_SEGMENTS[update.message.text])
    await update.message.reply_text(
        "Подобраны источники для данного сегмента",
        reply_markup=ReplyKeyboardMarkup(
            [['Начать расчет'],['/cancel']], resize_keyboard=True
        )
    )
    filters = Filters(update.effective_chat.id).to_dict()
    UserManager.set_sources(update.effective_chat.id, filter_sources(filters['age'], filters['gender'], filters['geo']))
    return TRENDS


async def start_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Начать расчет':
        get_trends_manager(update, context)
    return ConversationHandler.END
    

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
    

conversation_segments = ConversationHandler(
        entry_points=[CommandHandler("select_segment", select_segment),
                      CommandHandler("get_trends", select_segment),
                      MessageHandler(filters.Regex(r'Выбрать сегмент'), select_segment)],
        states={
            TOPIC: [
                MessageHandler(filters.TEXT, set_topic),
                CommandHandler("cancel", cancel),
            ],
            AGE: [
                MessageHandler(filters.TEXT, set_age),
                CommandHandler("cancel", cancel),
            ],
            GENDER: [
                MessageHandler(filters.TEXT, set_gender),
                CommandHandler("cancel", cancel),
            ],
            GEO: [
                MessageHandler(filters.TEXT, set_geo),
                CommandHandler("cancel", cancel),
            ],
            TRENDS: [
                MessageHandler(filters.TEXT, start_trends),
                CommandHandler("cancel", cancel),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
