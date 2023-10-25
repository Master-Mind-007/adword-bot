#!/usr/bin/env python3
from tzlocal import get_localzone
from pytz import timezone
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client as tgClient, enums
from asyncio import Lock
from dotenv import load_dotenv, dotenv_values
from threading import Thread
from time import sleep, time
from subprocess import Popen, run as srun
from os import remove as osremove, path as ospath, environ, getcwd
from faulthandler import enable as faulthandler_enable
from socket import setdefaulttimeout
from logging import getLogger, Formatter, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from uvloop import install

faulthandler_enable()
install()
setdefaulttimeout(600)
botStartTime = time()

basicConfig(format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s', handlers=[FileHandler('log.txt'), StreamHandler()], level=INFO)
LOGGER = getLogger(__name__)
log_info('Starting Configuration...')

load_dotenv('config.env', override=True)

ads = {}
user_data = {}
extra_buttons = {}
bot_cache = {}
non_queued_dl = set()
non_queued_up = set()
download_dict_lock = Lock()
status_reply_dict_lock = Lock()
queue_dict_lock = Lock()
qb_listener_lock = Lock()
status_reply_dict = {}

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
	log_error('BOT_TOKEN not found! Exiting...')
	exit(1)

bot_id = BOT_TOKEN.split(':', 1)[0]

OWNER_ID = environ.get('OWNER_ID', '')
if len(OWNER_ID) == 0:
	log_error("OWNER_ID variable is missing! Exiting now")
	exit(1)
else:
	OWNER_ID = int(OWNER_ID)

TELEGRAM_API = environ.get('TELEGRAM_API', '')
if len(TELEGRAM_API) == 0:
	log_error("TELEGRAM_API variable is missing! Exiting now")
	exit(1)
else:
	TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
if len(TELEGRAM_HASH) == 0:
	log_error("TELEGRAM_HASH variable is missing! Exiting now")
	exit(1)

TIMEZONE = environ.get('TIMEZONE', '')
if len(TIMEZONE) == 0:
	TIMEZONE = 'Asia/Kolkata'

def changetz(*args):
	return datetime.now(timezone(TIMEZONE)).timetuple()
Formatter.converter = changetz
log_info("TIMEZONE synced with logging status")

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
	for id_ in BLACKLIST_USERS.split():
		user_data[int(id_.strip())] = {'is_blacklist': True}

IS_PREMIUM_USER = False
user = ''
USER_SESSION_STRING = environ.get('USER_SESSION_STRING', '')
if len(USER_SESSION_STRING) != 0:
	log_info("Creating client from USER_SESSION_STRING")
	try:
		user = tgClient('user', TELEGRAM_API, TELEGRAM_HASH, session_string=USER_SESSION_STRING, workers=1000,
						parse_mode=enums.ParseMode.HTML).start()
		IS_PREMIUM_USER = user.me.is_premium
	except Exception as e:
		log_error(f"Failed making client from USER_SESSION_STRING : {e}")
		user = ''
	

AUTO_DELETE_MESSAGE_DURATION = environ.get('AUTO_DELETE_MESSAGE_DURATION', '')
if len(AUTO_DELETE_MESSAGE_DURATION) == 0:
	AUTO_DELETE_MESSAGE_DURATION = 30
else:
	AUTO_DELETE_MESSAGE_DURATION = int(AUTO_DELETE_MESSAGE_DURATION)

CMD_SUFFIX = environ.get('CMD_SUFFIX', '')

BASE_URL_PORT = environ.get('BASE_URL_PORT', '')
BASE_URL_PORT = 80 if len(BASE_URL_PORT) == 0 else int(BASE_URL_PORT)

BASE_URL = environ.get('BASE_URL', '').rstrip("/")
if len(BASE_URL) == 0:
	log_warning('BASE_URL not provided!')
	BASE_URL = ''

FSUB_IDS = environ.get('FSUB_IDS', '')
if len(FSUB_IDS) == 0:
	FSUB_IDS = ''

LOG_ID = environ.get('LOG_ID', '')
if len(LOG_ID) == 0:
	LOG_ID = ''
else:
	LOG_ID = int(LOG_ID)

BOT_PM = environ.get('BOT_PM', '')
BOT_PM = BOT_PM.lower() == 'true'

COVER_IMAGE = environ.get('COVER_IMAGE', '')
if len(COVER_IMAGE) == 0:
	COVER_IMAGE = 'https://telegra.ph/file/c012a278990265404207e.jpg'

SET_COMMANDS = environ.get('SET_COMMANDS', '')
SET_COMMANDS = SET_COMMANDS.lower() == 'true'

config_dict = {'AUTHORIZED_CHATS': AUTHORIZED_CHATS,
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
				'USER': user}

if BASE_URL:
	Popen(
		f"gunicorn web.wserver:app --bind 0.0.0.0:{BASE_URL_PORT} --worker-class gevent", shell=True)
try:
	log_info("Creating client from BOT_TOKEN")
	bot = tgClient('bot', TELEGRAM_API, TELEGRAM_HASH, bot_token=BOT_TOKEN, workers=1000,
				parse_mode=enums.ParseMode.HTML).start()
except Exception as e:
	log_error(f'Error Occured in Creating Bot Client! Verify BOT_TOKEN! Exiting... {e}')
	exit(1)

bot_loop = bot.loop
bot_name = bot.me.username
scheduler = AsyncIOScheduler(timezone=str(
	get_localzone()), event_loop=bot_loop)