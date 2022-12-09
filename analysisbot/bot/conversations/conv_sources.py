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
from analysisbot.bot.user import UserManager


def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

INPUT_PROCESSING = range(1)

async def set_sources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    reply_keyboard = [['/default', '/cancel']]
    await update.message.reply_text(
        text=TXT_SOURCES,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: {}".format(DEFAULT_SOURCES), resize_keyboard=True
        ),
    )
    return INPUT_PROCESSING


async def set_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input = update.message.text
    input = input.split()
    # usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_sources(update.effective_chat.id, input)
    await update.message.reply_text(
        "Список источников изменен",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
        
    
async def set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_sources(update.effective_chat.id, DEFAULT_SOURCES)
    # usr = User(update.effective_chat.id)
    # usr.get_from_db()
    # usr.sources = DEFAULT_SOURCES
    # usr.save_to_db()
    await update.message.reply_text(
        "Установлен список источников по умолчанию",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
    
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Не внесено изменений",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
    

conversation_sources = ConversationHandler(
        entry_points=[CommandHandler("set_sources", set_sources)],
        states={
            INPUT_PROCESSING: [
                CommandHandler("default", set_default),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
