#!/usr/bin/env python3
from time import time, monotonic
from datetime import datetime
from sys import executable
from os import execl as osexecl
from asyncio import create_subprocess_exec, gather
from cloudscraper import create_scraper

from requests import get as rget
from pytz import timezone as ptimezone
from bs4 import BeautifulSoup
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from aiofiles import open as aiopen
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, private, regex
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from worker import bot, bot_name, config_dict, user_data, botStartTime, LOGGER, scheduler
from worker.version import get_version
from .helper.ext_utils.fs_utils import start_cleanup, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_time, cmd_exec, sync_to_async, new_task, set_commands, update_user_ldata, get_stats, verifyChannel
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, editReplyMarkup, sendFile, deleteMessage, delete_all_messages, sendCustomMsg
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .helper.ext_utils.help_messages import help_string
from .helper.themes import BotTheme
from .modules import authorize, shell, eval, bot_settings, speedtest, gen_pyro_sess, adword

COVER_IMAGE = config_dict['COVER_IMAGE']

@new_task
async def start(client, message):
	buttons = ButtonMaker()
	buttons.ubutton("Owner", f"tg://user?id={config_dict['OWNER_ID']}")
	reply_markup = buttons.build_menu(1)
	if len(message.command) > 1 and message.command[1] == "adwx":
		await deleteMessage(message)
	elif await CustomFilters.authorized(client, message):
		start_string = BotTheme('ST_MSG', help_command=f"/{BotCommands.HelpCommand}")
		await sendMessage(message, start_string, reply_markup, photo=COVER_IMAGE)
	elif config_dict['BOT_PM']:
		await sendMessage(message, BotTheme('ST_BOTPM'), reply_markup, photo=COVER_IMAGE)
	else:
		await sendMessage(message, BotTheme('ST_UNAUTH'), reply_markup, photo=COVER_IMAGE)


async def restart(client, message):
	restart_message = await sendMessage(message, BotTheme('RESTARTING'))
	if scheduler.running:
		scheduler.shutdown(wait=False)
	await delete_all_messages()
	proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn')
	await gather(proc1.wait())
	async with aiopen(".restartmsg", "w") as f:
		await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
	osexecl(executable, executable, "-m", "worker")


async def welcome_master():
	if not await aiopath.isfile(".restartmsg"):
		msg, btns = await get_stats()
		text = "𝐀𝐃𝐰𝐨𝐫𝐝 𝐢𝐬 𝐔𝐏!"
		await sendCustomMsg(chat_id=config_dict['OWNER_ID'], buttons=btns, text=text, photo=COVER_IMAGE)


async def ping(_, message):
	start_time = monotonic()
	reply = await sendMessage(message, BotTheme('PING'))
	end_time = monotonic()
	await editMessage(reply, BotTheme('PING_VALUE', value=int((end_time - start_time) * 1000)))


async def log(_, message):
	owner = config_dict['OWNER_ID']
	buttons = ButtonMaker()
	buttons.ibutton('📑 Log Display', f'adwx {owner} logdisplay')
	buttons.ibutton('📨 Web Paste', f'adwx {owner} webpaste')
	await sendFile(message, 'log.txt', buttons=buttons.build_menu(1))


async def bot_help(client, message):
	buttons = ButtonMaker()
	user_id = message.from_user.id
	buttons.ibutton('Basic', f'adwx {user_id} guide basic')
	buttons.ibutton('Users', f'adwx {user_id} guide users')
	buttons.ibutton('Mics', f'adwx {user_id} guide miscs')
	buttons.ibutton('Owner & Sudos', f'adwx {user_id} guide admin')
	buttons.ibutton('Close', f'adwx {user_id} close')
	await sendMessage(message, "<b><i>𝐇𝐞𝐥𝐩 𝐆𝐮𝐢𝐝𝐞 𝐌𝐞𝐧𝐮!</i></b>\n\n<b>NOTE: <i>Click on any CMD to see more minor detalis.</i></b>", buttons.build_menu(2))


async def restart_notification():
	now = datetime.now(ptimezone(config_dict['TIMEZONE']))
	if await aiopath.isfile(".restartmsg"):
		with open(".restartmsg") as f:
			chat_id, msg_id = map(int, f)
	else:
		chat_id, msg_id = 0, 0

	if await aiopath.isfile(".restartmsg"):
		try:
			await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=BotTheme('RESTART_SUCCESS', time=now.strftime('%I:%M:%S %p'), date=now.strftime('%d/%m/%y'), timz=config_dict['TIMEZONE'], version=get_version()))
			if chat_id != config_dict['OWNER_ID']:
				text = "𝐀𝐃𝐰𝐨𝐫𝐝 𝐢𝐬 𝐔𝐏!"
				await sendCustomMsg(chat_id=config_dict['OWNER_ID'], text=text, photo=COVER_IMAGE)
		except Exception as e:
			LOGGER.error(e)
		await aioremove(".restartmsg")


async def stats(client, message):
    msg, btns = await get_stats(message)
    await sendMessage(message, msg, btns)


@new_task
async def handlex(_, query):
    message = query.message
    user_id = query.from_user.id
    data = query.data.split()
    if user_id != int(data[1]):
        return await query.answer(text="Not Yours!", show_alert=True)
    elif data[2] == "logdisplay":
        await query.answer()
        async with aiopen('log.txt', 'r') as f:
            logFileLines = (await f.read()).splitlines()
        def parseline(line):
            try:
                return "[" + line.split('] [', 1)[1]
            except IndexError:
                return line
        ind, Loglines = 1, ''
        try:
            while len(Loglines) <= 3500:
                Loglines = parseline(logFileLines[-ind]) + '\n' + Loglines
                if ind == len(logFileLines): 
                    break
                ind += 1
            startLine = f"<b>Showing Last {ind} Lines from log.txt:</b> \n\n----------<b>START LOG</b>----------\n\n"
            endLine = "\n----------<b>END LOG</b>----------"
            btn = ButtonMaker()
            btn.ibutton('Cʟᴏsᴇ', f'adwx {user_id} close')
            await sendMessage(message, startLine + escape(Loglines) + endLine, btn.build_menu(1))
            await editReplyMarkup(message, None)
        except Exception as err:
            LOGGER.error(f"TG Log Display : {str(err)}")
    elif data[2] == "webpaste":
        await query.answer()
        async with aiopen('log.txt', 'r') as f:
            logFile = await f.read()
        cget = create_scraper().request
        resp = cget('POST', 'http://stashbin.xyz/api/document', data={'content': logFile}).json()
        if resp['ok']:
            btn = ButtonMaker()
            btn.ubutton('📨 Web Paste', f"http://stashbin.xyz/{resp['data']['key']}")
            await editReplyMarkup(message, btn.build_menu(1))
    elif data[2] == "botpm":
        await query.answer(url=f"https://t.me/{bot_name}?start=adwx")
    elif data[2] == "help":
        await query.answer()
        btn = ButtonMaker()
        btn.ibutton('Cʟᴏsᴇ', f'adwx {user_id} close')
    elif data[2] == "guide":
        btn = ButtonMaker()
        btn.ibutton('Bᴀᴄᴋ', f'adwx {user_id} guide home')
        btn.ibutton('Cʟᴏsᴇ', f'adwx {user_id} close')
        if data[3] == "basic":
            await editMessage(message, help_string[0], btn.build_menu(2))
        elif data[3] == "users":
            await editMessage(message, help_string[1], btn.build_menu(2))
        elif data[3] == "miscs":
            await editMessage(message, help_string[3], btn.build_menu(2))
        elif data[3] == "admin":
            if not await CustomFilters.sudo('', query):
                return await query.answer('Not Sudo or Owner!', show_alert=True)
            await editMessage(message, help_string[2], btn.build_menu(2))
        else:
            buttons = ButtonMaker()
            buttons.ibutton('Basic', f'adwx {user_id} guide basic')
            buttons.ibutton('Users', f'adwx {user_id} guide users')
            buttons.ibutton('Mics', f'adwx {user_id} guide miscs')
            buttons.ibutton('Owner & Sudos', f'adwx {user_id} guide admin')
            buttons.ibutton('Close', f'adwx {user_id} close')
            await editMessage(message, "<b><i>𝐇𝐞𝐥𝐩 𝐆𝐮𝐢𝐝𝐞 𝐌𝐞𝐧𝐮!</i></b>\n\n<b>NOTE: <i>Click on any CMD to see more minor detalis.</i></b>", buttons.build_menu(2))
        await query.answer()
    elif data[2] == "stats":
        msg, btn = await get_stats(query, data[3])
        await editMessage(message, msg, btn, COVER_IMAGE)
    elif data[2] == "close":
        await query.answer()
        await deleteMessage(message)
        if message.reply_to_message:
            await deleteMessage(message.reply_to_message)
            if message.reply_to_message.reply_to_message:
                await deleteMessage(message.reply_to_message.reply_to_message)
    else:
        await query.answer()
        await deleteMessage(message)
        if message.reply_to_message:
            await deleteMessage(message.reply_to_message)
            if message.reply_to_message.reply_to_message:
                await deleteMessage(message.reply_to_message.reply_to_message)


async def main():
	await gather(verifyChannel(bot), start_cleanup(), welcome_master(), restart_notification(), set_commands(bot))
	
	bot.add_handler(MessageHandler(
		start, filters=command(BotCommands.StartCommand) & private))
	bot.add_handler(MessageHandler(log, filters=command(
		BotCommands.LogCommand) & CustomFilters.sudo))
	bot.add_handler(MessageHandler(restart, filters=command(
		BotCommands.RestartCommand) & CustomFilters.sudo))
	bot.add_handler(MessageHandler(ping, filters=command(
		BotCommands.PingCommand) & CustomFilters.authorized & ~CustomFilters.blacklisted))
	bot.add_handler(MessageHandler(bot_help, filters=command(
		BotCommands.HelpCommand) & CustomFilters.authorized & ~CustomFilters.blacklisted))
	bot.add_handler(MessageHandler(stats, filters=command(
	    BotCommands.StatsCommand) & CustomFilters.authorized & ~CustomFilters.blacklisted))
	bot.add_handler(CallbackQueryHandler(handlex, filters=regex(r'^adwx')))
	LOGGER.info(f"ADWORDS [@{bot_name}] is Up!")
	signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
