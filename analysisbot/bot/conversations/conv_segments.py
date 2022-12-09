# from datetime import timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

from analysisbot.bot.constants import *
from analysisbot.bot.user import UserManager, Filters
from analysisbot.bot.segments import *
from analysisbot.bot.conversations.get_trends_manager import get_trends_manager
from analysisbot.logging.logger import _logger

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
        await update.message.reply_text(
            "Подобраны источники для данного сегмента",
            reply_markup=ReplyKeyboardMarkup(
                [['Расчитать тренды'],['/cancel']], resize_keyboard=True
            )
        )
        return TRENDS
        
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
    Filters.set_gender(update.effective_chat.id, GENDER_SEGMENTS[update.message.text])
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
            [['Расчитать тренды'],['/cancel']], resize_keyboard=True
        )
    )
    filters = Filters(update.effective_chat.id).to_dict()
    _logger.info(filters)
    source_list = filter_sources(tuple(filters['age']), filters['gender'], filters['geo'])
    _logger.info(source_list)
    UserManager.set_sources(update.effective_chat.id, source_list)
    
    return ConversationHandler.END


# async def start_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.message.text == 'Расчитать тренды':
#         await get_trends_manager(update, context)
#     else:
#         await update.message.reply_text(
#             "Отмена",
#             reply_markup=ReplyKeyboardMarkup(
#                 [['Выбрать сегмент']], resize_keyboard=True
#             )
#         )
#     return ConversationHandler.END
    

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отмена",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD, resize_keyboard=True
        )
    )
    return ConversationHandler.END
    

conversation_segments = ConversationHandler(
        entry_points=[CommandHandler("select_segment", select_segment, block=False),
                      CommandHandler("get_trends", select_segment, block=False),
                      MessageHandler(filters.Regex('Выбрать сегмент'), select_segment, block=False)],
        states={
            TOPIC: [
                MessageHandler(filters.TEXT, set_topic, block=False),
                CommandHandler("cancel", cancel, block=False),
            ],
            AGE: [
                MessageHandler(filters.TEXT, set_age, block=False),
                CommandHandler("cancel", cancel, block=False),
            ],
            GENDER: [
                MessageHandler(filters.TEXT, set_gender, block=False),
                CommandHandler("cancel", cancel, block=False),
            ],
            GEO: [
                MessageHandler(filters.TEXT, set_geo, block=False),
                CommandHandler("cancel", cancel, block=False),
            ],
            # TRENDS: [
            #     MessageHandler(filters.TEXT, start_trends),
            #     CommandHandler("cancel", cancel),
            # ]
        },
        fallbacks=[CommandHandler("cancel", cancel, block=False)],
    )
