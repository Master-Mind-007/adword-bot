#!/usr/bin/env python3
import platform
from datetime import datetime
from os import path as ospath
from aiofiles import open as aiopen
from aiofiles.os import remove as aioremove, path as aiopath, mkdir
from re import match as re_match
from time import time
from psutil import disk_usage, disk_io_counters, Process, cpu_percent, swap_memory, cpu_count, cpu_freq, getloadavg, virtual_memory, net_io_counters, boot_time
from asyncio import create_subprocess_exec, create_subprocess_shell, run_coroutine_threadsafe, sleep
from asyncio.subprocess import PIPE
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession as aioClientSession
from psutil import virtual_memory, cpu_percent, disk_usage
from sys import exit as sexit

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import BadRequest
from pyrogram.types import BotCommand
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.filters import command, regex, create
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.raw.functions.channels import GetChannels

from worker.helper.themes import BotTheme
from worker import OWNER_ID, bot_name, bot_cache, LOGGER, download_dict_lock, botStartTime, user_data, config_dict, bot_loop, extra_buttons, user, bot
from worker.helper.telegram_helper.bot_commands import BotCommands
from worker.helper.telegram_helper.button_build import ButtonMaker

THREADPOOL   = ThreadPoolExecutor(max_workers=1000)
URL_REGEX    = r'^(?!\/)(rtmps?:\/\/|mms:\/\/|rtsp:\/\/|https?:\/\/|ftp:\/\/)?([^\/:]+:[^\/@]+@)?(www\.)?(?=[^\/:\s]+\.[^\/:\s]+)([^\/:\s]+\.[^\/:\s]+)(:\d+)?(\/[^#\s]*[\s\S]*)?(\?[^#\s]*)?(#.*)?$'
SIZE_UNITS   = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
STATUS_START = 0
PAGES        = 1
PAGE_NO      = 1


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.task = bot_loop.create_task(self.__set_interval())

    async def __set_interval(self):
        while True:
            await sleep(self.interval)
            await self.action()

    def cancel(self):
        self.task.cancel()


def handleIndex(index, dic):
    while True:
        if abs(index) >= len(dic):
            if index < 0: index = len(dic) - abs(index)
            elif index > 0: index = index - len(dic)
        else: break
    return index


def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes}B'


async def download_image_url(url):
    path = "Images/"
    if not await aiopath.isdir(path):
        await mkdir(path)
    image_name = url.split('/')[-1]
    des_dir = ospath.join(path, image_name)
    async with aioClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiopen(des_dir, 'wb') as file:
                    async for chunk in response.content.iter_chunked(1024):
                        await file.write(chunk)
                LOGGER.info(f"Image Downloaded Successfully as {image_name}")
            else:
                LOGGER.error(f"Failed to Download Image from {url}")
    return des_dir


async def turn_page(data):
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    global STATUS_START, PAGE_NO
    async with download_dict_lock:
        if data[1] == "nex":
            if PAGE_NO == PAGES:
                STATUS_START = 0
                PAGE_NO = 1
            else:
                STATUS_START += STATUS_LIMIT
                PAGE_NO += 1
        elif data[1] == "pre":
            if PAGE_NO == 1:
                STATUS_START = STATUS_LIMIT * (PAGES - 1)
                PAGE_NO = PAGES
            else:
                STATUS_START -= STATUS_LIMIT
                PAGE_NO -= 1


def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result


def update_user_ldata(id_, key=None, value=None):
    exception_keys = ['is_sudo', 'is_auth', 'dly_tasks', 'is_blacklist']
    if key is None and value is None:
        if id_ in user_data:
            updated_data = {}
            for k, v in user_data[id_].items():
                if k in exception_keys:
                    updated_data[k] = v
            user_data[id_] = updated_data
        return
    user_data.setdefault(id_, {})
    user_data[id_][key] = value


def get_progress_bar_string(pct):
    pct = float(str(pct).strip('%'))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    cPart = int(p % 8 - 1)
    p_str = '■' * cFull
    if cPart >= 0:
        p_str += ['▤', '▥', '▦', '▧', '▨', '▩', '■'][cPart]
    p_str += '□' * (12 - cFull)
    return f"[{p_str}]"

    
async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper


async def sync_to_async(func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    future = bot_loop.run_in_executor(THREADPOOL, pfunc)
    return await future if wait else future


def async_to_sync(func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future


def new_thread(func):
    @wraps(func)
    def wrapper(*args, wait=False, **kwargs):
        future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
        return future.result() if wait else future
    return wrapper


async def get_stats(event=None, key="home"):
    user_id = event.from_user.id if event != None else config_dict['OWNER_ID']
    btns = ButtonMaker()
    btns.ibutton('Back', f'adwx {user_id} stats home')
    if key == "home":
        btns = ButtonMaker()
        btns.ibutton('Bot Stats', f'adwx {user_id} stats stbot')
        btns.ibutton('OS Stats', f'adwx {user_id} stats stsys')
        msg = "⌬ <b><i>Bot & OS Statistics!</i></b>"
    elif key == "stbot":
        total, used, free, disk = disk_usage('/')
        swap = swap_memory()
        memory = virtual_memory()
        disk_io = disk_io_counters()
        msg = BotTheme('BOT_STATS',
            bot_uptime=get_readable_time(time() - botStartTime),
            ram_bar=get_progress_bar_string(memory.percent),
            ram=memory.percent,
            ram_u=get_readable_file_size(memory.used),
            ram_f=get_readable_file_size(memory.available),
            ram_t=get_readable_file_size(memory.total),
            swap_bar=get_progress_bar_string(swap.percent),
            swap=swap.percent,
            swap_u=get_readable_file_size(swap.used),
            swap_f=get_readable_file_size(swap.free),
            swap_t=get_readable_file_size(swap.total),
            disk=disk,
            disk_bar=get_progress_bar_string(disk),
            disk_read=get_readable_file_size(disk_io.read_bytes) + f" ({get_readable_time(disk_io.read_time / 1000)})" if disk_io else "Access Denied",
            disk_write=get_readable_file_size(disk_io.write_bytes) + f" ({get_readable_time(disk_io.write_time / 1000)})" if disk_io else "Access Denied",
            disk_t=get_readable_file_size(total),
            disk_u=get_readable_file_size(used),
            disk_f=get_readable_file_size(free),
        )
    elif key == "stsys":
        cpuUsage = cpu_percent(interval=0.5)
        msg = BotTheme('SYS_STATS',
            os_uptime=get_readable_time(time() - boot_time()),
            os_version=platform.version(),
            os_arch=platform.platform(),
            up_data=get_readable_file_size(net_io_counters().bytes_sent),
            dl_data=get_readable_file_size(net_io_counters().bytes_recv),
            pkt_sent=str(net_io_counters().packets_sent)[:-3],
            pkt_recv=str(net_io_counters().packets_recv)[:-3],
            tl_data=get_readable_file_size(net_io_counters().bytes_recv + net_io_counters().bytes_sent),
            cpu=cpuUsage,
            cpu_bar=get_progress_bar_string(cpuUsage),
            cpu_freq=f"{cpu_freq(percpu=False).current / 1000:.2f} GHz" if cpu_freq() else "Access Denied",
            sys_load="%, ".join(str(round((x / cpu_count() * 100), 2)) for x in getloadavg()) + "%, (1m, 5m, 15m)",
            p_core=cpu_count(logical=False),
            v_core=cpu_count(logical=True) - cpu_count(logical=False),
            total_core=cpu_count(logical=True),
            cpu_use=len(Process().cpu_affinity()),
        )
    btns.ibutton('Close', f'adwx {user_id} close')
    return msg, btns.build_menu(2)


async def set_commands(client):
    if config_dict['SET_COMMANDS']:
        try:
            bot_cmds = [
            BotCommand(BotCommands.StartCommand, f'Start the bot.'),
            BotCommand(BotCommands.HelpCommand, 'Get detailed help about the Bot'),
            BotCommand(BotCommands.AdwordCommand[0], f'or /{BotCommands.AdwordCommand[1]} ADword Settings'),
            BotCommand(BotCommands.StatsCommand[0], f'or /{BotCommands.StatsCommand[1]} Check Bot & System stats'),
            BotCommand(BotCommands.SpeedCommand[0], f'or /{BotCommands.SpeedCommand[1]} Check Server Up & Down Speed & Details'),
            BotCommand(BotCommands.BotSetCommand[0], f"or /{BotCommands.BotSetCommand[1]} Bot's Personal Settings (Owner or Sudo Only)"),
            BotCommand(BotCommands.RestartCommand[0], f'or /{BotCommands.RestartCommand[1]} Restart & Update the Bot (Owner or Sudo Only)'),
            ]
            LOGGER.info('Bot Commands have been Set & Updated')
        except Exception as err:
            LOGGER.error(err)

async def verifyChannel(client):
    if config_dict['LOG_ID'] != '':
        try:
            me = await client.get_chat_member(config_dict['LOG_ID'], "me")
            if me.privileges:
                if not me.privileges.can_post_messages:
                    LOGGER.error("Cannot Send Messages in Logs Channel!")
                    sexit(0)
            else:
                group = await client.invoke(GetChannels(id=[await client.resolve_peer(config_dict['LOG_ID'])]))
                restrictions = group.chats[0].default_banned_rights.send_messages
                if me.status == ChatMemberStatus.MEMBER and restrictions:
                    LOGGER.error("Cannot Send Messages in Logs Group!")
                    sexit(0)
            msg = await client.send_message(chat_id=config_dict['LOG_ID'], text="Logger Started!")
        except BadRequest as e:
            if 'CHANNEL_INVALID' in str(e):
                LOGGER.error("Bot Not in the Logs Channel!")
            elif 'CHANNEL_PRIVATE' in str(e):
                LOGGER.error("Logs Channel is Private!")
            elif 'USER_BANNED_IN_CHANNEL' in str(e):
                LOGGER.error("Bot is Banned in Logs Channel!")
            elif 'USER_BOT' in str(e):
                LOGGER.error("Bot is Not Admin in Logs Channel!")
            else:
                LOGGER.error(e)
            sexit(0)
        except Exception as e:
            LOGGER.error(e)
    else:
        LOGGER.error("LOG_ID not found!")
        sexit(0)