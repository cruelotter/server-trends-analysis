from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import asyncio

from myapp.logging.logger import _logger
from myapp.model.pipeline import Pipeline
from myapp.bot.user import User, UserManager
from myapp.bot.constants import *


def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

async def get_trends_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    _logger.warning('Pipeline started')
    chat_id = update.effective_message.chat_id
    
    await context.bot.send_message(chat_id, text=f"Модель запущена. Пожалуйста, подождите, процесс сбора и обработки данных может занять длительное время")
    usr = UserManager.get_from_db(chat_id)
    _logger.warning([chat_id, usr.history_duration, usr.trend_period, usr.sources])
    pipeline = Pipeline(chat_id, usr.history_duration, usr.trend_period, usr.sources)
    file, trends = pipeline.run()
    await context.bot.send_document(chat_id, document=open(file+".html", 'rb'),
                                    caption=trends.to_string(),
                                    reply_markup=ReplyKeyboardMarkup(
            [['/get_trends']], resize_keyboard=True
        ))
    _logger.warning("Pipeline ran successfully")
    # await context.bot.send_message(chat_id, text=f"Обработка завершена успешно!\n{trends}")
    