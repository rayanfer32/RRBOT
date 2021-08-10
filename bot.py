#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv("secrets.env") 

import logging
import os
import time
from functools import wraps
import random
import threading
from datetime import datetime

print("Loading Bot Modules...")
import delegator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
from telegram.ext.dispatcher import run_async

import settings

# # override settings is local settings exist
# import sys
# sys.path.append("~/")
# import rrbot_settings as settings

# Enable logging
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


__tasks = set()

bot = Bot(settings.TOKEN)

undeliveredMessages = []
def average(lst): 
    return sum(lst) / len(lst) 

def notifyUsers(msg):
  logger.info(msg)
  for user_id in settings.ENABLED_USERS:
    bot.send_message(user_id,msg)


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in settings.ENABLED_USERS:
            print(f"Unauthorized access denied for {user_id}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@restricted
def start(update, context):
    def to_buttons(cmd_row):
        return [InlineKeyboardButton(e[0], callback_data=e[1]) for e in cmd_row]
    keyboard = [
        to_buttons(row) for row in settings.SC_MENU_ITEM_ROWS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = ("Your inputs are shell commands.\r\n"
           "Supported commands:\r\n"
           "/script to run scripts in ./scripts directory\r\n"
           "/tasks to show all running tasks\r\n"
           "/sudo_login to call sudo\r\n"
           "/kill to kill a running task\r\n"
           "Shortcut:")
    update.message.reply_text(msg, reply_markup=reply_markup)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def __is_out_all(cmd: str) -> (str,bool):
    param = 'oa;'
    if cmd.startswith(param):
        return cmd[len(param):], True
    return cmd, True # True for always out all

@run_async
def __do_exec(cmd, update, context, is_script=False, need_filter_cmd=True):
    message = update.message or update.callback_query.message
    reply_text = message.reply_text  # to hold func reply_text
    logger.debug('exec command "%s", is_script "%s"', cmd, is_script)

    max_idx = 3
    cmd, is_out_all = __is_out_all(cmd)
    if is_out_all:
        max_idx = 999999

    if need_filter_cmd and not __check_cmd_chars(cmd):
        reply_text(f'This cmd is illegal.')
        return

    if is_script:
        cmd = os.path.join(settings.SCRIPTS_ROOT_PATH, cmd)

    try:
        c = delegator.run(cmd, block=False, timeout=1e6)
    except FileNotFoundError as e:
        reply_text(f"{e}")
        return
    out = ''
    task = (f'{c.pid}', cmd, c)
    __tasks.add(task)
    start_time = time.time()
    idx = 0

    for line in c.subprocess:
        out += line
        cost_time = time.time() - start_time
        if cost_time > 1:
            reply_text(out[:settings.MAX_TASK_OUTPUT])
            idx += 1
            out = ''
            start_time = time.time()
        if idx > max_idx:
            reply_text(f'Command not finished. You can kill it by sending /kill {c.pid}')
            break
    c.block()

    __tasks.remove(task)
    if out:
        reply_text(out[:settings.MAX_TASK_OUTPUT])
    if idx > 3:
        reply_text(f'Task finished: {cmd}')


def __do_cd(update, context):
    cmd: str = update.message.text
    if not cmd.startswith('cd '):
        return False
    try:
        os.chdir(cmd[3:])
        update.message.reply_text(f'pwd: {os.getcwd()}')
    except FileNotFoundError as e:
        update.message.reply_text(f'{e}')
    return True


def __check_cmd(cmd: str):
    cmd = cmd.lower()
    if cmd.startswith('sudo'):
        cmd = cmd[4:].strip()
    cmd = cmd.split(' ')[0]
    if settings.CMD_WHITE_LIST and cmd not in settings.CMD_WHITE_LIST:
        return False
    if cmd in settings.CMD_BLACK_LIST:
        return False
    return True


def __check_cmd_chars(cmd: str):
    for char in settings.CMD_BLACK_CHARS:
        if char in cmd:
            return False
    return True


@restricted
def do_exec(update, context):
    if not update.message:
        return
    if __do_cd(update, context):
        return
    cmd: str = update.message.text
    if not __check_cmd(cmd):
        return
    __do_exec(cmd, update, context)


@restricted
def do_tasks(update, context):
    msg = '\r\n'.join([', '.join(e[:2]) for e in __tasks])
    if not msg:
        msg = "Task list is empty"
    update.message.reply_text(msg)


@restricted
def do_script(update, context):
    args = context.args.copy()
    if args:
        cmd = ' '.join(args)
        __do_exec(cmd, update, context, is_script=True)
        return
    scripts = '\r\n'.join(
        os.path.join(r[len(settings.SCRIPTS_ROOT_PATH):], file)
        for r, d, f in os.walk(settings.SCRIPTS_ROOT_PATH) for file in f
    )
    msg = "Usage: /script script_name args\r\n"
    msg += scripts
    update.message.reply_text(msg)


@restricted
def do_kill(update, context):
    if not context.args:
        update.message.reply_text('Usage: /kill pid')
        return

    pid = context.args[0]
    for task in __tasks:
        if task[0] == pid:
            task[2].kill()
            update.message.reply_text(f'killed: {task[1]}')
            return
    update.message.reply_text(f'pid "{pid}" not find')


@restricted
def do_sudo_login(update, context):
    if not context.args:
        update.message.reply_text('Usage: /sudo_login password')
        return

    password = context.args[0]
    c = delegator.chain(f'echo "{password}" | sudo -S xxxvvv')
    out = c.out
    if 'xxxvvv: command not found' in out:
        update.message.reply_text(f'sudo succeeded.')
    update.message.reply_text(f'sudo failed.')


@restricted
def shortcut_cb(update, context):
    query = update.callback_query
    cmd = query.data
    if cmd not in settings.SC_MENU_ITEM_CMDS.keys():
        update.callback_query.message.reply_text(f'This cmd is illegal.')
    cmd_info = settings.SC_MENU_ITEM_CMDS[cmd]
    is_script = cmd_info[2] if len(cmd_info) >= 3 else False
    __do_exec(cmd, update, context, is_script=is_script, need_filter_cmd=False)


def main():
    updater = Updater(
        settings.TOKEN, use_context=True,
        request_kwargs=settings.REQUEST_KWARGS
    )

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CallbackQueryHandler(shortcut_cb))

    dp.add_handler(CommandHandler("tasks", do_tasks))
    dp.add_handler(CommandHandler("kill", do_kill, pass_args=True))

    if not settings.ONLY_SHORTCUT_CMD:
        dp.add_handler(CommandHandler("sudo_login", do_sudo_login, pass_args=True))
        dp.add_handler(CommandHandler("script", do_script, pass_args=True))
        dp.add_handler(MessageHandler(Filters.text, do_exec))

    dp.add_error_handler(error)
    updater.start_polling()
    logger.info('Telegram shell bot started.')
    notifyUsers('Telegram shell bot started.')
    updater.idle()

def packetLossNotifier():
    import subprocess
    import re
    logger.info("packetLossNotifier Started.")
    max_latency = -1.0
    packetLoss = 0.0
    serverId = 0 # counter for picking server sequentially

    def isSleepTime():
        return (now.hour >= settings.PINGER_SLEEP_AT or now.hour < settings.PINGER_RESUME_AT)
        
    def calcSleepDurHours(now):
        # this func only works if isSleepTime is true otherwise returns a negative value
        if now < settings.PINGER_SLEEP_AT:
            return (settings.PINGER_RESUME_AT - now) * 3600
        else:
            return ( (24- now) + settings.PINGER_RESUME_AT ) *3600

    while True:
        # check for sleep time
        now = datetime.now()
        
        if(isSleepTime()):
            try:
                sleepDuration = calcSleepDurHours(now.hour)
                notifyUsers(f"packetLossNotifier on Sleep for next {sleepDuration} hours.")
                time.sleep(sleepDuration) # sleep the thread for remaining hours
                notifyUsers("packetLossNotifier Resumed.")
            except Exception as e:
                logger.info(e)

        pingServers = settings.PING_SERVERS

        # Increment serverId
        server = pingServers[serverId]
        if serverId == len(pingServers) - 1:
            serverId = 0
        else:
            serverId += 1 

        try:
            response = subprocess.Popen(
                ['ping', '-c', '60', server], # send 60 pings to server
                stderr=subprocess.STDOUT,  # get all output
                stdout=subprocess.PIPE,
                universal_newlines=True  # return string not bytes
            )
        except subprocess.CalledProcessError:
            response = None

        max_latency = 0
        latencies = []

        try:
            for line in response.stdout:
                if 'packet loss' in line:
                # print(line.find('packet loss'))
                    packetLoss = float(line[len('received,')+line.find('received,'):line.find('% packet loss')])
                if 'time=' in line:
                    latencyStr = line[len('time=')+line.find('time='):]
                    latencyStr = re.sub('ms','',latencyStr)
                    latency = float(latencyStr)
                    latencies.append(latency)
            packetLoss = round(packetLoss)
            max_latency = round(average(latencies))
        except Exception as e:
            logger.error(f"{e} line: {line}")

        logger.info(f"Server:{server},Latency:{max_latency}ms,Loss:{packetLoss}%")

        msg = None
        if (packetLoss > settings.PACKETLOSS_ALERT):
            msg = '⚠️' * 5 +'\n'
            msg += f"{packetLoss}% Packet Loss while pinging {server}\n"
            msg += f"{max_latency}ms Latency Detected!"
        elif (max_latency > settings.LATENCY_ALERT):
            msg = '⏰' * 5 + '\n'
            msg += 'High Latency.\n'
            msg += f"{max_latency}ms Latency Detected while pinging {server}"

        global undeliveredMessages
        if msg != None:
            try:
                notifyUsers(msg)
            except:
                logger.info(f"Undelivered message: {msg}")
                undeliveredMessages.append(msg)

        if undeliveredMessages != []:
            try:
                for failedMsg in undeliveredMessages:
                    notifyUsers(failedMsg)
                undeliveredMessages = []
            except:
                logger.info(f"Failed to deliver {failedMsg}")

    logger.info("packetLossNotifier has Stopped!.")
    notifyUsers("packetLossNotifier has Stopped!.")

if __name__ == '__main__':
  threading.Thread(target=packetLossNotifier,daemon=True).start()
  main()