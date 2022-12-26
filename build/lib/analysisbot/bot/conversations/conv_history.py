# from datetime import timedelta
# from dateutil.relativedelta import relativedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from analysisbot.bot.constants import *
from analysisbot.bot.user import UserManager

def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

INPUT_PROCESSING = range(1)

async def set_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    reply_keyboard = OPTIONS_HISTORY
    reply_keyboard.append(['/default', '/cancel'])
    await update.message.reply_text(
        text=TXT_HISTORY,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="default: 2 года", resize_keyboard=True
        ),
    )
    return INPUT_PROCESSING


async def set_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = 12
    if update.message.text == "1 год":
        history = 12*1
    elif update.message.text == "3 года":
        history = 12*3
    elif update.message.text == "6 месяцев":
        history = 6
    elif update.message.text == "5 лет":
        history = 12*5
    else:
        await update.message.reply_text(
            "Ошибка, такой вариант не предусмотрен",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    UserManager.set_history_duration(update.effective_chat.id, history)

    await update.message.reply_text(
        f"Теперь будет использоваться история за {update.message.text}",
        reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        )
    )
    return ConversationHandler.END
        
    
async def set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # usr = UserManager.get_from_db(update.effective_chat.id)
    UserManager.set_history_duration(update.effective_chat.id, DEFAULT_HISTORY)
   
    await update.message.reply_text(
        "Теперь будет использоваться история за 2 года",
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
    

conversation_history = ConversationHandler(
        entry_points=[CommandHandler("set_history", set_history)],
        states={
            INPUT_PROCESSING: [
                CommandHandler("default", set_default),
                CommandHandler("cancel", cancel),
                MessageHandler(filters.TEXT, set_custom),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
