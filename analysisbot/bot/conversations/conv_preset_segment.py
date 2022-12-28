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


SEG, TYPE = range(2)

# async def select_segment()


async def preset_segment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return ConversationHandler.END
    SegmentManager.check_base(update.effective_chat.id)
    segment_lst = SegmentManager.get_user_segments(update.effective_chat.id)
    for segment in segment_lst:
        print(segment['name'])
    reply_keyboard = [[key['name']] for key in SegmentManager.get_user_segments(update.effective_chat.id)]
    reply_keyboard.append(['/cancel'])
    await update.message.reply_text(
        text="Выберите сегмент или нажмите /cancel для отмены",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return SEG
        
    
async def set_segment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text
    id, sources = SegmentManager.get_preset_sources(update.effective_chat.id, name)
    UserManager.set_sources(update.effective_chat.id, id, sources.split())
    await update.message.reply_text(
        "Подобраны источники для данного сегмента",
        reply_markup=ReplyKeyboardMarkup(
            [['Расчитать тренды'],['/cancel']], resize_keyboard=True
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


conversation_preset_segments = ConversationHandler(
        entry_points=[#CommandHandler("select_segment", preset_segment, block=False),
                      #CommandHandler("get_trends", select_segment, block=False),
                      MessageHandler(filters.Regex('Выбрать из пресетов'), preset_segment, block=False)],
        states={
            SEG: [
                MessageHandler(filters.TEXT, set_segment, block=False),
                CommandHandler("cancel", cancel, block=False),
            ],
            # TYPE: [
            #     MessageHandler(filters.TEXT, set_gender, block=False),
            #     CommandHandler("cancel", cancel, block=False),
            # ],
        },
        fallbacks=[CommandHandler("cancel", cancel, block=False)],
    )