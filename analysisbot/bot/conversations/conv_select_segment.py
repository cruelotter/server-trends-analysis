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


TOPIC, TYPE = range(2)

# async def select_segment()


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
        return ConversationHandler.END
        
    Filters.set_topic(update.effective_chat.id, TOPIC_SEGMENTS[update.message.text])
    
    await update.message.reply_text(
        "Выберите способ настройки сегмента",
        reply_markup=ReplyKeyboardMarkup(
            [[key] for key in TYPE_OF_CHOICE.keys()], resize_keyboard=True
        )
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отмена",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD, resize_keyboard=True
        )
    )
    return ConversationHandler.END


conversation_choice_segments = ConversationHandler(
        entry_points=[CommandHandler("select_segment", select_segment, block=False),
                      CommandHandler("get_trends", select_segment, block=False),
                      MessageHandler(filters.Regex('Выбрать сегмент'), select_segment, block=False)],
        states={
            TOPIC: [
                MessageHandler(filters.TEXT, set_topic, block=False),
                # CommandHandler("cancel", cancel, block=False),
            ],
            # TYPE: [
            #     MessageHandler(filters.TEXT, set_gender, block=False),
            #     CommandHandler("cancel", cancel, block=False),
            # ],
        },
        fallbacks=[CommandHandler("cancel", cancel, block=False)],
    )