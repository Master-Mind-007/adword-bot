#!/usr/bin/env python3
from random import choice
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, regex, create
from pyrogram.enums import ChatType
from functools import partial
from collections import OrderedDict
from asyncio import create_subprocess_exec, create_subprocess_shell, sleep
from aiofiles.os import remove, rename, path as aiopath
from aiofiles import open as aiopen
from os import environ, getcwd
from dotenv import load_dotenv
from time import time
from io import BytesIO
from aioshutil import rmtree as aiormtree
from pyrogram import Client as tgClient, enums

from worker import bot, config_dict, user_data, status_reply_dict_lock, IS_PREMIUM_USER, LOGGER
from worker.helper.telegram_helper.message_utils import sendMessage, sendFile, editMessage, deleteMessage
from worker.helper.telegram_helper.filters import CustomFilters
from worker.helper.telegram_helper.bot_commands import BotCommands
from worker.helper.telegram_helper.button_build import ButtonMaker
from worker.helper.ext_utils.bot_utils import sync_to_async, new_thread
from worker.helper.ext_utils.help_messages import default_desp
from worker.helper.themes import AVL_THEMES

START = 0
STATE = 'view'
handler_dict = {}
default_values = {'AUTO_DELETE_MESSAGE_DURATION': 30,
				  'DOWNLOAD_DIR': '/usr/src/app/downloads/',
				  'STATUS_UPDATE_INTERVAL': 10,
				  'SEARCH_LIMIT': 0,
				  'UPSTREAM_BRANCH': 'master',
				  'BOT_THEME': 'minimal',
				  'BOT_LANG': 'en',
				  'IMG_PAGE': 1,
				  }
bool_vars = ['AS_DOCUMENT', 'BOT_PM', 'SET_COMMANDS', 'SOURCE_LINK', 'SHOW_EXTRA_CMDS', 'CLEAN_LOG_MSG','INCOMPLETE_TASK_NOTIFIER']


async def load_config():

	BOT_TOKEN = environ.get('BOT_TOKEN', '')
	if len(BOT_TOKEN) == 0:
		BOT_TOKEN = config_dict['BOT_TOKEN']

	TELEGRAM_API = environ.get('TELEGRAM_API', '')
	if len(TELEGRAM_API) == 0:
		TELEGRAM_API = config_dict['TELEGRAM_API']
	else:
		TELEGRAM_API = int(TELEGRAM_API)

	TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
	if len(TELEGRAM_HASH) == 0:
		TELEGRAM_HASH = config_dict['TELEGRAM_HASH']

	BOT_MAX_TASKS = environ.get('BOT_MAX_TASKS', '')
	BOT_MAX_TASKS = int(BOT_MAX_TASKS) if BOT_MAX_TASKS.isdigit() else ''
	
	OWNER_ID = environ.get('OWNER_ID', '')
	OWNER_ID = config_dict['OWNER_ID'] if len(OWNER_ID) == 0 else int(OWNER_ID)

	DOWNLOAD_DIR = environ.get('DOWNLOAD_DIR', '')
	if len(DOWNLOAD_DIR) == 0:
		DOWNLOAD_DIR = '/usr/src/app/downloads/'
	elif not DOWNLOAD_DIR.endswith("/"):
		DOWNLOAD_DIR = f'{DOWNLOAD_DIR}/'

	AUTHORIZED_CHATS = environ.get('AUTHORIZED_CHATS', '')
	if len(AUTHORIZED_CHATS) != 0:
		aid = AUTHORIZED_CHATS.split()
		for id_ in aid:
			user_data[int(id_.strip())] = {'is_auth': True}

	SUDO_USERS = environ.get('SUDO_USERS', '')
	if len(SUDO_USERS) != 0:
		aid = SUDO_USERS.split()
		for id_ in aid:
			user_data[int(id_.strip())] = {'is_sudo': True}
			
	BLACKLIST_USERS = environ.get('BLACKLIST_USERS', '')
	if len(BLACKLIST_USERS) != 0:
		aid = BLACKLIST_USERS.split()
		for id_ in aid:
			user_data[int(id_.strip())] = {'is_blacklist': True}

	CMD_SUFFIX = environ.get('CMD_SUFFIX', '')

	USER_SESSION_STRING = environ.get('USER_SESSION_STRING', '')

	BASE_URL_PORT = environ.get('BASE_URL_PORT', '')
	BASE_URL_PORT = 80 if len(BASE_URL_PORT) == 0 else int(BASE_URL_PORT)

	await (await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")).wait()
	BASE_URL = environ.get('BASE_URL', '').rstrip("/")
	if len(BASE_URL) == 0:
		BASE_URL = ''
	else:
		await create_subprocess_shell(f"gunicorn web.wserver:app --bind 0.0.0.0:{BASE_URL_PORT} --worker-class gevent")

	FSUB_IDS = environ.get('FSUB_IDS', '')
	if len(FSUB_IDS) == 0:
		FSUB_IDS = ''

	LOG_ID = environ.get('LOG_ID', '')
	if len(LOG_ID) == 0:
		LOG_ID = ''

	BOT_PM = environ.get('BOT_PM', '')
	BOT_PM = BOT_PM.lower() == 'true'

	COVER_IMAGE = environ.get('COVER_IMAGE', '')
	if len(COVER_IMAGE) == 0:
		COVER_IMAGE = 'https://graph.org/file/60f9f8bcb97d27f76f5c0.jpg'

	SET_COMMANDS = environ.get('SET_COMMANDS', '')
	SET_COMMANDS = SET_COMMANDS.lower() == 'true'
	
	
	TIMEZONE = environ.get('TIMEZONE', '')
	if len(TIMEZONE) == 0:
		TIMEZONE = 'Asia/Kolkata'
		
	config_dict.update({'AUTHORIZED_CHATS': AUTHORIZED_CHATS,
					'AUTO_DELETE_MESSAGE_DURATION': AUTO_DELETE_MESSAGE_DURATION,
					'BASE_URL': BASE_URL,
					'BASE_URL_PORT': BASE_URL_PORT,
					'BLACKLIST_USERS': BLACKLIST_USERS,
					'BOT_TOKEN': BOT_TOKEN,
					'BOT_PM': BOT_PM,
					'CMD_SUFFIX': CMD_SUFFIX,
					'COVER_IMAGE': COVER_IMAGE,
					'DOWNLOAD_DIR': DOWNLOAD_DIR,
					'FSUB_IDS': FSUB_IDS,
					'LOG_ID': LOG_ID,
					'OWNER_ID': OWNER_ID,
					'SET_COMMANDS': SET_COMMANDS,
					'SUDO_USERS': SUDO_USERS,
					'TELEGRAM_API': TELEGRAM_API,
					'TELEGRAM_HASH': TELEGRAM_HASH,
					'TIMEZONE': TIMEZONE,
					'USER_SESSION_STRING': USER_SESSION_STRING,
					'USER': user})


async def get_buttons(key=None, edit_type=None, edit_mode=None, mess=None):
	buttons = ButtonMaker()
	if key is None:
		buttons.ibutton('⚙️ CONFIGURATION ⚙️', "botset var")
		buttons.ibutton('Exit', "botset close")
		msg = '<b><i>Bot Settings:</i></b>'
	elif key == 'var':
		for k in list(OrderedDict(sorted(config_dict.items())).keys())[START:10+START]:
			buttons.ibutton(k, f"botset editvar {k}")
		buttons.ibutton('Back', "botset back")
		buttons.ibutton('Close', "botset close")
		for x in range(0, len(config_dict)-1, 10):
			buttons.ibutton(f'{int(x/10)+1}', f"botset start var {x}", position='footer')
		msg = f'<b>Config Variables</b> | <b>Page: {int(START/10)+1}</b>'
	elif edit_type == 'editvar':
		msg = f'<b>Variable:</b> <code>{key}</code>\n\n'
		msg += f'<b>Description:</b> {default_desp.get(key, "No Description Provided")}\n\n'
		if mess.chat.type == ChatType.PRIVATE:
			msg += f'<b>Value:</b> {config_dict.get(key, "None")} \n\n'
		else:
			buttons.ibutton('View Var Value',
							f"botset showvar {key}", position="header")
		buttons.ibutton('Back', "botset back var", position="footer")
		if key not in bool_vars:
			if not edit_mode:
				buttons.ibutton('Edit Value', f"botset editvar {key} edit")
			else:
				buttons.ibutton('Stop Edit', f"botset editvar {key}")
		if key not in ['TELEGRAM_HASH', 'TELEGRAM_API', 'OWNER_ID', 'BOT_TOKEN'] and key not in bool_vars:
			buttons.ibutton('Reset', f"botset resetvar {key}")
		buttons.ibutton('Close', "botset close", position="footer")
		if edit_mode and key in ['SUDO_USERS', 'CMD_SUFFIX', 'OWNER_ID', 'USER_SESSION_STRING', 'TELEGRAM_HASH',
								 'TELEGRAM_API', 'AUTHORIZED_CHATS', 'BOT_TOKEN', 'DOWNLOAD_DIR']:
			msg += '<b>Note:</b> Restart required for this edit to take effect!\n\n'
		if edit_mode and key not in bool_vars:
			msg += '<i>Send a valid value for the above Var.</i> <b>Timeout:</b> 60 sec'
		if key in bool_vars:
			msg += '<i>Choose a valid value for the above Var</i>'
			buttons.ibutton('True', f"botset boolvar {key} on")
			buttons.ibutton('False', f"botset boolvar {key} off")
	button = buttons.build_menu(1) if key is None else buttons.build_menu(2)
	return msg, button


async def update_buttons(message, key=None, edit_type=None, edit_mode=None):
	msg, button = await get_buttons(key, edit_type, edit_mode, message)
	await editMessage(message, msg, button)


async def edit_variable(_, message, pre_message, key):
	handler_dict[message.chat.id] = False
	value = message.text
	if key == 'DOWNLOAD_DIR':
		if not value.endswith('/'):
			value += '/'
	elif key == 'LINKS_LOG_ID':
		value = int(value)
	elif key == 'BOT_THEME':
		if not value.strip() in AVL_THEMES.keys():
			value = 'minimal'
	elif key == 'BASE_URL_PORT':
		value = int(value)
		if config_dict['BASE_URL']:
			await (await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")).wait()
			await create_subprocess_shell(f"gunicorn web.wserver:app --bind 0.0.0.0:{value} --worker-class gevent")
	elif value.isdigit():
		value = int(value)
	elif key == 'USER_SESSION_STRING':
		if len(value) != 0:
			LOGGER.info("Creating client from USER_SESSION_STRING")
			try:
				global user
				user = tgClient('user', config_dict['TELEGRAM_API'], config_dict['TELEGRAM_HASH'], session_string=value, workers=1000,
								parse_mode=enums.ParseMode.HTML)
				await user.start()
				IS_PREMIUM_USER = user.me.is_premium
				config_dict['USER'] = user
			except Exception as e:
				LOGGER.error(f"Failed making client from USER_SESSION_STRING : {e}")
				user = ''
	config_dict[key] = value
	await update_buttons(pre_message, key, 'editvar', False)
	await deleteMessage(message)


async def event_handler(client, query, pfunc, rfunc, document=False):
	chat_id = query.message.chat.id
	handler_dict[chat_id] = True
	start_time = time()

	async def event_filter(_, __, event):
		user = event.from_user or event.sender_chat
		return bool(user.id == query.from_user.id and event.chat.id == chat_id and (event.text or event.document and document))
	handler = client.add_handler(MessageHandler(
		pfunc, filters=create(event_filter)), group=-1)
	
	while handler_dict[chat_id]:
		await sleep(0.5)
		if time() - start_time > 60:
			handler_dict[chat_id] = False
			await rfunc()
	client.remove_handler(*handler)


@new_thread
async def edit_bot_settings(client, query):
	data = query.data.split()
	message = query.message
	if data[1] == 'close':
		handler_dict[message.chat.id] = False
		await query.answer()
		await deleteMessage(message)
		await deleteMessage(message.reply_to_message)
	elif data[1] == 'back':
		handler_dict[message.chat.id] = False
		await query.answer()
		key = data[2] if len(data) == 3 else None
		if key is None:
			globals()['START'] = 0
		await update_buttons(message, key)
	elif data[1] == 'var':
		await query.answer()
		await update_buttons(message, data[1])
	elif data[1] == 'resetvar':
		handler_dict[message.chat.id] = False
		await query.answer('Reset Done!', show_alert=True)
		value = ''
		if data[2] == 'BASE_URL':
			await (await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")).wait()
		elif data[2] == 'BASE_URL_PORT':
			value = 80
			if config_dict['BASE_URL']:
				await (await create_subprocess_exec("pkill", "-9", "-f", "gunicorn")).wait()
				await create_subprocess_shell("gunicorn web.wserver:app --bind 0.0.0.0:80 --worker-class gevent")
		config_dict[data[2]] = value
		await update_buttons(message, data[2], 'editvar', False)
	elif data[1] == 'boolvar':
		handler_dict[message.chat.id] = False
		value = data[3] == "on"
		await query.answer(f'Successfully Var changed to {value}!', show_alert=True)
		config_dict[data[2]] = value
		await update_buttons(message, data[2], 'editvar', False)
	elif data[1] == 'editvar':
		handler_dict[message.chat.id] = False
		await query.answer()
		edit_mode = len(data) == 4
		await update_buttons(message, data[2], data[1], edit_mode)
		if data[2] in bool_vars or not edit_mode:
			return
		pfunc = partial(edit_variable, pre_message=message, key=data[2])
		rfunc = partial(update_buttons, message, data[2], data[1], edit_mode)
		await event_handler(client, query, pfunc, rfunc)

	elif data[1] == 'showvar':
		value = config_dict[data[2]]
		if len(str(value)) > 200:
			await query.answer()
			with BytesIO(str.encode(value)) as out_file:
				out_file.name = f"{data[2]}.txt"
				await sendFile(message, out_file)
			return
		elif value == '':
			value = None
		await query.answer(f'{value}', show_alert=True)
	elif data[1] == 'edit':
		await query.answer()
		globals()['STATE'] = 'edit'
		await update_buttons(message, data[2])
	elif data[1] == 'view':
		await query.answer()
		globals()['STATE'] = 'view'
		await update_buttons(message, data[2])
	elif data[1] == 'start':
		await query.answer()
		if START != int(data[3]):
			globals()['START'] = int(data[3])
			await update_buttons(message, data[2])

async def bot_settings(_, message):
	msg, button = await get_buttons()
	globals()['START'] = 0
	await sendMessage(message, msg, button, config_dict['COVER_IMAGE'])


bot.add_handler(MessageHandler(bot_settings, filters=command(
	BotCommands.BotSetCommand) & CustomFilters.sudo))
bot.add_handler(CallbackQueryHandler(edit_bot_settings,
				filters=regex("^botset") & CustomFilters.sudo))
