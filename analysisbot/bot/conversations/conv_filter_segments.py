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


AGE, GENDER, GEO = range(3)

# async def select_segment()


async def start_filter_segment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
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
    source_list = SegmentManager.get_filtered_sources(filters['age'], filters['gender'], filters['geo'])
    # source_list = filter_sources(tuple(filters['age']), filters['gender'], filters['geo'])
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
    

conversation_filter_segments = ConversationHandler(
        entry_points=[#CommandHandler("select_segment", start_filter_segment, block=False),
                      #CommandHandler("get_trends", start_filter_segment, block=False),
                      MessageHandler(filters.Regex('Выбрать по фильтрам'), start_filter_segment, block=False)],
        states={
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
        },
        fallbacks=[CommandHandler("cancel", cancel, block=False)],
    )
