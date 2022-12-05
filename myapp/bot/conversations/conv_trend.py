from datetime import timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from myapp.bot.constants import *
from myapp.bot.user import UserManager


def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

INPUT_PROCESSING = range(1)

async def set_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    reply_keyboard = OPTIONS_TREND
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_TREND,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 7 дней"
        ),
    )
    return INPUT_PROCESSING


async def set_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match(update.message.text):
        case "За 1 месяц":
            trend = 30
        case "За 2 недели":
            trend = 14
        case "За 1 неделю":
            trend = 7
        case "За 2 дня":
            trend = 2
    # usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_trend_period(update.effective_chat.id, trend)
    # usr = User(update.effective_chat.id)
    # usr.get_from_db()
    # usr.trend_period = trend
    # usr.save_to_db()
    await update.message.reply_text(
        f"Будут выявляться тренды за {update.message.text}",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
        
    
async def set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_trend_period(update.effective_chat.id, DEFAULT_TREND)
    # usr = User(update.effective_chat.id)
    # usr.get_from_db()
    # usr.trend_period = DEFAULT_TREND
    # usr.save_to_db()
    await update.message.reply_text(
        "Будут выявляться тренды за 7 дней",
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
    

conversation_trend = ConversationHandler(
        entry_points=[CommandHandler("set_trend", set_trend)],
        states={
            INPUT_PROCESSING: [
                CommandHandler("default", set_default),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
