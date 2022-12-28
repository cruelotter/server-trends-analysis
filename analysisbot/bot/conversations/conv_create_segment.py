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

NAME, LIST = range(2)


async def create_segment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    reply_keyboard = [['/cancel']]
    await update.message.reply_text(
        text="Введите название сегмента",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return NAME


async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text
    SegmentManager.exist(update.effective_chat.id, name)
    context.user_data['name'] = name
    reply_keyboard = [['/cancel']]
    await update.message.reply_text(
        text=TXT_SOURCES,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: {}".format(DEFAULT_SOURCES), resize_keyboard=True
        ),
    )
    return LIST


async def set_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input = update.message.text
    input = input.split()
    segment_id = SegmentManager.set_sources_custom(update.effective_chat.id, context.user_data['name'], input)
    # usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_sources(update.effective_chat.id, segment_id, input)
    # SegmentManager.set_sources_custom
    await update.message.reply_text(
        "Список источников изменен",
        reply_markup=ReplyKeyboardMarkup(
            [['Расчитать тренды'],['/cancel']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
        
    
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Не внесено изменений",
        reply_markup=ReplyKeyboardMarkup(
            [['Расчитать тренды'],['/cancel']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
    

conversation_create_segment = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Создать свой сегмент"), create_segment)],
        states={
            NAME: [
                # CommandHandler("default", set_default),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_name),
            ],
            LIST: [
                MessageHandler(filters.TEXT, set_list)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
