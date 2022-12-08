import toml
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from myapp.model import *
from myapp.bot.user import UserManager
from myapp.bot.constants import *
from myapp.bot.conversations import *
from myapp.logging.logger import _logger

import nest_asyncio
nest_asyncio.apply()

def check_access(username):
    whitelist = set(line.strip() for line in open('users_whitelist.txt'))
    if username in whitelist:
        return True
    else: return False

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not check_access(update.effective_user.username):
#         await context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=ACCEESS_DENIED.format(update.effective_user.username)
#         )
#         return
#     await context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=ACCEESS_GRANTED
#         )
#     username = update.effective_user.full_name
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=TXT_START.format(username)
#     )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TXT_HELP.format(update.effective_user.full_name)
    )
    
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    usr = UserManager.get_from_db(update.effective_chat.id)
    status = usr.status
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Current status: {STATUS_TYPES[status]}"
    )
    
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.username):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ACCEESS_DENIED.format(update.effective_user.username)
        )
        return
    usr = UserManager.get_from_db(update.effective_chat.id)
    _logger.warning(usr.to_dict())
    # usr = User(update.effective_chat.id)
    # usr.get_from_db()
    dstr = usr.schedule_days.split()
    weekdays = {0: 'Вс', 1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб'}
    days = [weekdays[int(d)] for d in dstr]
    days_str = ' '.join(days)
    src = '\n' + usr.sources.replace(' ', '\n')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=PROFILE.format(usr.id, usr.history_duration, usr.trend_period, days_str, usr.schedule_time[:-3], src),
        disable_web_page_preview=True
    )
    
# def rerun_schedule(context: ContextTypes.DEFAULT_TYPE):
#     all = UserManager.get_all()
#     for usr in all:
#         current_jobs = context.job_queue.get_jobs_by_name(str(usr['_id']))
#         if current_jobs:
#             for job in current_jobs:
#                 job.schedule_removal()
        
#         sd = usr['schedule_days']
#         if not sd == "":
#             days = sd.split()
#             t_days = tuple([int(d) for d in days])
#             context.job_queue.run_daily(get_trends_manager, chat_id=usr['_id'], name=str(usr['_id']), time=time().fromisoformat(usr['schedule_time']), days=t_days)


async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ERROR
    )
    e = context.error
    e_text = []
    trace = e.__traceback__
    trace_str = '{}    {},   line {}'
    while trace is not None:
        e_text.append(trace_str.format(trace.tb_frame.f_code.co_filename, trace.tb_frame.f_code.co_name, trace.tb_lineno))
        trace = trace.tb_next
    traces = "\n".join(e_text)
    txt = f'''{type(e).__name__}
{e}
{traces}'''
    _logger.error(txt)
    await context.bot.send_message(
        chat_id=957739166,
        text=txt
    )
    return txt

if __name__ == '__main__':
    
    config = toml.load('config.toml')['telegram-bot']
    bot_token = config['bot_token']
    app = ApplicationBuilder().token(bot_token).build()
    
    help_handler = CommandHandler('help', help, block=False)
    app.add_handler(help_handler, 1)
    
    status_handler = CommandHandler('status', status, block=False)
    app.add_handler(status_handler, 0)
    
    profile_handler = CommandHandler('profile', profile, block=False)
    app.add_handler(profile_handler, 3)
    
    get_trends_handler = CommandHandler('get_trends', get_trends_manager, block=False)
    app.add_handler(get_trends_handler, 4)
    
    app.add_handler(conversation_segments)
    app.add_handlers([conversation_start, conversation_sources, conversation_history,
                      conversation_trend, conversation_schedule, ])
    
    app.add_error_handler(error)
    
    app.run_polling(drop_pending_updates=True)