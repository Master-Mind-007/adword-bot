#!/usr/bin/env python3

######################################################
# AUTHOR: MIKHIL
# TELEGRAM: @MASTERMIND_MIKHIL @MASTERMIKHIL
# PROJECT: ADWORD
# DISTRIBUTION IS PROHIBITED WITHOUT PREMISSION
######################################################

from random import choice as rchoice
from functools import partial
from time import time
from asyncio import sleep as asleep, create_task as createTask, CancelledError
from collections import OrderedDict

from pyrogram.filters import create
from pyrogram.enums import ChatType
from pyrogram.handlers import MessageHandler
from pyrogram.raw.functions.channels import GetChannels, GetForumTopics
from pyrogram.raw.types import ForumTopic, ForumTopicDeleted
from pyrogram.raw.functions.messages import ForwardMessages

from worker import user_data, bot, config_dict, ads, LOGGER
from worker.helper.telegram_helper.message_utils import editMessage, deleteMessage, sendCustomMsg
from worker.helper.telegram_helper.button_build import ButtonMaker

tasks = {}
groups = {}
handler_dict = {}
settings = {'interval': 2, 'logging': 'normal'}


class adVert:
	def __init__(self, ad_id=None):
		self.ad_id = ad_id

	def add(self):
		ad_id = ''.join(rchoice('1234567890abcdefghijklmnopqrstuvwxyz') for _ in range(8))
		if ad_id in ads:
			ad_id = ''.join(rchoice('1234567890abcdefghijklmnopqrstuvwxyz') for _ in range(8))
		ads[ad_id] = {
			'name': f"Advert {len(ads)+1}",
			'enabled': False,
			'msg' : '',
			'interval': 1800,
			'sender': 'bot',
			'mode': 'send',
			'web_preview': False
		}
		LOGGER.info(f"Added AD: {self.ad_id}")

	def remove(self):
		if self.ad_id in ads:
			ads.pop(self.ad_id)
			LOGGER.info(f"Removed AD: {self.ad_id}")


class adTaskHandler:
	def __init__(self, ad_id):
		self.ad_id = ad_id
		self.bot = bot
		self.user = config_dict['USER']

	async def log(self, message):
		if config_dict['LOG_ID'] != '':
			await sendCustomMsg(chat_id=config_dict['LOG_ID'], text=message)

	async def sendMsg(self, chat_id, message, sender, web_preview=False, reply_to_message_id=False, debug=True):
		app = self.bot if sender == "bot" else self.user
		message_conf = {'chat_id': chat_id}
		try:
			if message.text:
				message_conf['text'] = message.text
			photo = message.photo.file_id if message.photo else ''
		except:
			pass
		if message.reply_markup:
			message_conf['reply_markup'] = message.reply_markup
		if reply_to_message_id:
			message_conf['reply_to_message_id'] = reply_to_message_id
		msg = ""
		try:
			if photo == '':
				if message.caption:
					message_conf['text'] = message.caption
				if message.entities:
					message_conf['entities'] = message.entities
				if web_preview:
					message_conf['disable_web_page_preview'] = not web_preview
				await app.send_message(**message_conf)
			else:
				if message.caption:
					message_conf['caption'] = message.caption
				if message.entities:
					message_conf['caption_entities'] = message.entities
				if photo != '':
					message_conf['photo'] = photo
				await app.send_photo(**message_conf)
			if settings['logging'] == "advanced" and debug:
				msg = f"𝐆𝐫𝐨𝐮𝐩 𝐍𝐚𝐦𝐞: {groups[chat_id]['name']}\n𝐓𝐨𝐩𝐢𝐜: {groups[chat_id]['forums'][reply_to_message_id]['name']}" if reply_to_message_id else f"𝐆𝐫𝐨𝐮𝐩 𝐍𝐚𝐦𝐞: {groups[chat_id]['name']}"
				await self.log(f"𝐒𝐮𝐜𝐜𝐞𝐬𝐬! 𝐀𝐝 𝐒𝐞𝐧𝐭!\n𝐀𝐃: {ads[self.ad_id]['name']}\n{msg}\n𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: {chat_id}")
			LOGGER.info(f"AD: {self.ad_id} | Sent to {chat_id}!")
			return "success"
		except Exception as e:
			if settings['logging'] == "advanced" and debug:
				msg = f"𝐆𝐫𝐨𝐮𝐩 𝐍𝐚𝐦𝐞: {groups[chat_id]['name']}\n𝐓𝐨𝐩𝐢𝐜: {groups[chat_id]['forums'][reply_to_message_id]['name']}" if reply_to_message_id else f"𝐆𝐫𝐨𝐮𝐩 𝐍𝐚𝐦𝐞: {groups[chat_id]['name']}"
				await self.log(f"𝐅𝐚𝐢𝐥𝐞𝐝!\n𝐀𝐃: {ads[self.ad_id]['name']}\n{msg}\n𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: {chat_id}\n𝐄𝐫𝐫𝐨𝐫: {str(e)}")
			LOGGER.error(f"AD: {self.ad_id} | Send to {chat_id} | Failed!")
			LOGGER.error(f"Error: {str(e)}")
			return "fail"


	async def forwardMsg(self, chat_id, message, sender, reply_to_message_id=False, debug=True):
		app = self.bot if sender == "bot" else self.user
		message_conf = {
		'from_peer': await app.resolve_peer(message.chat.id),
		'to_peer': await app.resolve_peer(chat_id),
		'id': [message.id],
		'random_id': [app.rnd_id()]
		}
		try:
			if reply_to_message_id:
				message_conf['top_msg_id'] = reply_to_message_id
		except:
			pass
		msg = ""
		try:
			await app.invoke(ForwardMessages(**message_conf))
			if settings['logging'] == "advanced" and debug:
				msg = f"𝐆𝐫𝐨𝐮𝐩 𝐍𝐚𝐦𝐞: {groups[chat_id]['name']}\n𝐓𝐨𝐩𝐢𝐜: {groups[chat_id]['forums'][reply_to_message_id]['name']}" if reply_to_message_id else f"𝐆𝐫𝐨𝐮𝐩 𝐍𝐚𝐦𝐞: {groups[chat_id]['name']}"
				await self.log(f"𝐒𝐮𝐜𝐜𝐞𝐬𝐬! 𝐀𝐝 𝐒𝐞𝐧𝐭!\n𝐀𝐃: {ads[self.ad_id]['name']}\n{msg}\n𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: {chat_id}")
			LOGGER.info(f"AD: {ads[self.ad_id]['name']} | Sent to {chat_id}!")
			return "success"
		except Exception as e:
			if settings['logging'] == "advanced" and debug:
				await self.log(f"𝐅𝐚𝐢𝐥𝐞𝐝!\n𝐀𝐃: {ads[self.ad_id]['name']}\n{msg}\n𝐆𝐫𝐨𝐮𝐩 𝐈𝐃: {chat_id}\n𝐄𝐫𝐫𝐨𝐫: {str(e)}")
			LOGGER.error(f"AD: {ads[self.ad_id]['name']} | Send to {chat_id} | Failed!")
			LOGGER.error(f"Error: {str(e)}")
			return "fail"

	async def task(self):
		try:
			while ads[self.ad_id]['enabled']:
				message = await sendCustomMsg(chat_id=config_dict['LOG_ID'], text=f"𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐒𝐞𝐧𝐝𝐢𝐧𝐠 𝐏𝐨𝐬𝐭𝐬!\n𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭: {ads[self.ad_id]['name']}") if settings['logging'] == 'normal' else ""
				success = 0
				fail = 0
				total_grp = 0
				for id, grp in groups.items():
					total_grp += 1 if not grp['blocked'] else 0
				try:
					for grp_id, group in list(groups.items()):
						if ads[self.ad_id]['enabled']:
							if not group['blocked']:
								if group['is_forum']:
									for id, topic in list(group['forums'].items()):
										if id in group['topic']:
											status = await self.sendMsg(grp_id, ads[self.ad_id]['msg'], ads[self.ad_id]['sender'], ads[self.ad_id]['web_preview'], reply_to_message_id=id) if ads[self.ad_id]['mode'] == 'send' else await self.forwardMsg(grp_id, ads[self.ad_id]['msg'], ads[self.ad_id]['sender'], reply_to_message_id=id)
											if status == "success":
												success += 1
											else:
												fail += 1
											await asleep(settings['interval'])
									if settings['logging'] == 'normal':
										await editMessage(message, text=f"𝐒𝐭𝐚𝐭𝐮𝐬: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠!\n𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭: {ads[self.ad_id]['name']}\n𝐓𝐨𝐭𝐚𝐥 𝐆𝐫𝐨𝐮𝐩𝐬: {total_grp}\n𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {success}\n𝐅𝐚𝐢𝐥𝐞𝐝: {fail}")
								else:
									status = await self.sendMsg(grp_id, ads[self.ad_id]['msg'], ads[self.ad_id]['sender'], ads[self.ad_id]['web_preview']) if ads[self.ad_id]['mode'] == 'send' else await self.forwardMsg(grp_id, ads[self.ad_id]['msg'], ads[self.ad_id]['sender'])
									if status == "success":
										success += 1
									else:
										fail += 1
									if settings['logging'] == 'normal':
										await editMessage(message, text=f"𝐒𝐭𝐚𝐭𝐮𝐬: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠!\n𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭: {ads[self.ad_id]['name']}\n𝐓𝐨𝐭𝐚𝐥 𝐆𝐫𝐨𝐮𝐩𝐬: {total_grp}\n𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {success}\n𝐅𝐚𝐢𝐥𝐞𝐝: {fail}")
									await asleep(settings['interval'])
					if settings['logging'] == 'normal':
						await editMessage(message, text=f"𝐒𝐭𝐚𝐭𝐮𝐬: 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝!\n𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭: {ads[self.ad_id]['name']}\n𝐓𝐨𝐭𝐚𝐥 𝐆𝐫𝐨𝐮𝐩𝐬: {total_grp}\n𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {success}\n𝐅𝐚𝐢𝐥𝐞𝐝: {fail}")
					LOGGER.info(f"AD: {self.ad_id} Sleeping for {ads[self.ad_id]['interval']}s!")
					await asleep(ads[self.ad_id]['interval'])
				except RuntimeError as e:
					LOGGER.error(e)
					await asleep(ads[self.ad_id]['interval'])
				except Exception as e:
					LOGGER.error(e)
		except CancelledError:
			LOGGER.error("Async Stopped UnExpectedly")
		except Exception as e:
			LOGGER.error(e)

	async def addTask(self):
		LOGGER.info(f"AD: {self.ad_id} | Started!")
		Task = createTask(self.task())
		tasks[self.ad_id] = Task

	async def removeTask(self):
		if self.ad_id in tasks:
			LOGGER.info(f"AD: {self.ad_id} | Stopped!")
			Task = tasks[self.ad_id]
			Task.cancel()

	async def stopallTasks(self):
		LOGGER.info(f"Stopped all Tasks!")
		for ad_id, Task in tasks.items():
			Task.cancel()


async def event_handler(bot, query, func):
	chat_id = query.message.chat.id
	handler_dict[chat_id] = True
	start_time = time()

	async def event_filter(_, __, event):
		user = event.from_user or event.sender_chat
		return bool(user.id == query.from_user.id and event.chat.id == chat_id and (event.text or event.caption))
	handler = bot.add_handler(MessageHandler(
		func, filters=create(event_filter)), group=-1)

	while handler_dict[chat_id]:
		await asleep(0.5)
		if time() - start_time > 60:
			handler_dict[chat_id] = False
	bot.remove_handler(*handler)


async def adword_conf(event, key, user, START=0):
	btns = ButtonMaker()
	if key =="home":
		btns.ibutton('⚙️ 𝐀𝐃 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒 ⚙️', f'adword {user} admenu')
		btns.ibutton("⚙️ 𝐆𝐑𝐎𝐔𝐏𝐒 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒 ⚙️", f'adword {user} chnl_set')
		btns.ibutton("⚙️ 𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐀𝐓𝐈𝐎𝐍 ⚙️", f'adword {user} conf')
		btns.ibutton('𝐂𝐋𝐎𝐒𝐄', f'adword {user} close', position='footer')
		return "", btns.build_menu(1)
	elif key == "conf" or key == "interval" or key == "logging":
		if key == "conf":
			btns.ibutton('𝐁𝐀𝐂𝐊', f'adword {user} conf home', position='footer')
			btns.ibutton('𝐂𝐋𝐎𝐒𝐄', f'adword {user} close', position='footer')
			btns.ibutton(f"⏰ 𝐈𝐧𝐭𝐞𝐫𝐯𝐚𝐥: {settings['interval']}s", f'adword {user} conf interval')
			btns.ibutton(f" 𝐋𝐨𝐠𝐠𝐢𝐧𝐠: {settings['logging']}", f'adword {user} conf logging')
			return "", btns.build_menu(1)
		elif key == "logging":
			settings[key] = "normal" if settings[key] == "advanced" else "advanced"
			return await adword_conf(event, "conf", user, START)
		else:
			message = event.message
			msg = f"<b>Send New:</b> <i>Interval</i>"
			btns.ibutton('𝐂𝐚𝐧𝐜𝐞𝐥', f'adword {user} conf interval')
			await editMessage(message, msg, btns.build_menu(1), config_dict['COVER_IMAGE'])
			async def edit_adword(_, message, pre_message):
				handler_dict[event.message.chat.id] = False
				settings['interval'] = int(message.text)
				await deleteMessage(message)
			func = partial(edit_adword, pre_message=message)
			await event_handler(bot, event, func)
			await editMessage(message, "", btns.build_menu(1), config_dict['COVER_IMAGE'])
			return await adword_conf(event, "conf", user, START)
	elif key == "admenu" or key == "add":
		msg = "<b>Configuring Adword Bot!</b>"
		btns.ibutton('➕ 𝐀𝐃𝐃', f'adword {user} conf add', position='header')
		btns.ibutton('🟩 𝐒𝐭𝐚𝐫𝐭 𝐀𝐥𝐥', f'adword {user} conf enableall')
		btns.ibutton('🟥 𝐒𝐭𝐨𝐩 𝐀𝐥𝐥', f'adword {user} conf disableall')
		btns.ibutton('𝐁𝐀𝐂𝐊', f'adword {user} conf home')
		btns.ibutton('𝐂𝐋𝐎𝐒𝐄', f'adword {user} close')
		if key == "add":
			add_ad = adVert()
			add_ad.add()
		for k in list(OrderedDict(ads.items()).keys())[START:10+START]:
			btns.ibutton(f"{'🟢' if ads[k]['enabled'] else '🔴'} {ads[k].get('name')}", f"adword {user} conf ad {k}")
		if len(ads) > 10:
			for x in range(0, len(ads)+1, 10):
				btns.ibutton(f'{int(x/10)+1}', f"adword {user} conf admenu page {x}", position='footer')
		return msg, btns.build_menu(2)
	elif key == "enableall" or key == "disableall":
		for ad_id, ad in ads.items():
			if key == "enableall" and ads[ad_id]['msg'] == "":
				await event.answer(text=f"AD: {ads[ad_id]['name']}\nEmpty Advertisement!", show_alert=True)
			else:
				ad['enabled'] = True if key == "enableall" else False
				run = adTaskHandler(ad_id)
				await run.addTask() if ad['enabled'] == True else await run.removeTask()
		return await adword_conf(event, "admenu", user, START)


async def adword_setup(event, ad_id, user):
	btns = ButtonMaker()
	for ad, info in ads.items():
		if ad_id == ad:
			if info['msg'] != '':
				btns.ibutton("👀 𝐕𝐢𝐞𝐰 𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭", f'adword {user} conf {ad_id} edit view', position='header')
				btns.ibutton("✒️ 𝐄𝐝𝐢𝐭 𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭", f'adword {user} conf {ad_id} edit msg', position='header')
			else:
				btns.ibutton("➕ 𝐀𝐝𝐝 𝐀𝐝𝐯𝐞𝐫𝐭𝐢𝐬𝐞𝐦𝐞𝐧𝐭", f'adword {user} conf {ad_id} edit msg', position='header')
			btns.ibutton(f"✒️ 𝐍𝐚𝐦𝐞: {info['name']}", f'adword {user} conf {ad_id} edit name')
			btns.ibutton("🟢 𝐄𝐧𝐚𝐛𝐥𝐞𝐝" if info['enabled'] else "🔴 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝", f'adword {user} conf {ad_id} edit enabled')
			btns.ibutton(f"⏰ 𝐈𝐧𝐭𝐞𝐫𝐯𝐚𝐥: {info['interval']}s", f'adword {user} conf {ad_id} edit interval')
			btns.ibutton(f"🌐 𝐖𝐞𝐛 𝐏𝐫𝐞𝐯𝐢𝐞𝐰: {info['web_preview']}", f'adword {user} conf {ad_id} edit web_preview')
			btns.ibutton(f"⚙️ 𝐌𝐨𝐝𝐞: {info['mode']}", f'adword {user} conf {ad_id} edit mode')
			btns.ibutton(f"{'🤖' if info['sender'] == 'bot' else '👤'} 𝐒𝐞𝐧𝐝𝐞𝐫: {info['sender']}", f'adword {user} conf {ad_id} edit sender')
			btns.ibutton(f"🗑 𝐃𝐞𝐥𝐞𝐭𝐞", f'adword {user} conf {ad_id} edit delete')
			btns.ibutton('𝐁𝐀𝐂𝐊', f'adword {user} conf admenu', position='footer')
			btns.ibutton('𝐂𝐋𝐎𝐒𝐄', f'adword {user} close', position='footer')
	return "", btns.build_menu(1)


async def adword_settings(event, ad_id, item, user):
	chat_id = event.message.chat.id
	if item == "msg" or item == "name" or item == "interval":
		message = event.message
		msg = "<b>Send or Forward your Advertisement.</b>" if item == "msg" else f"<b>Send New:</b> <i>{item.upper()}</i>"
		btns = ButtonMaker()
		btns.ibutton('𝐂𝐚𝐧𝐜𝐞𝐥', f'adword {user} conf ad {ad_id}')
		await editMessage(message, msg, btns.build_menu(1), config_dict['COVER_IMAGE'])
		async def edit_adword(_, message, pre_message, ad_id, _item):
			if item == "interval":
				try:
					ads[ad_id][_item] = int(message.text)
				except:
					pass
			elif item == "msg":
				msg = await bot.forward_messages(chat_id=config_dict['LOG_ID'], from_chat_id=message.chat.id, message_ids=message.id)
				ads[ad_id][_item] = await bot.get_messages(config_dict['LOG_ID'], msg.id)
			else:
				ads[ad_id][_item] = message.text
			handler_dict[chat_id] = False
			await deleteMessage(message)
		func = partial(edit_adword, pre_message=message, ad_id=ad_id, _item=item)
		await event_handler(bot, event, func)
	elif item == "view":
		sender = adTaskHandler(ad_id)
		await sender.sendMsg(chat_id, ads[ad_id]['msg'], "bot", ads[ad_id]['web_preview'], debug=False) if ads[ad_id]['mode'] == "send" else await sender.forwardMsg(chat_id, ads[ad_id]['msg'], "bot", debug=False)
	elif item == "enabled":
		ads[ad_id][item] = True if ads[ad_id][item] == False else False
		run = adTaskHandler(ad_id)
		if ads[ad_id][item] == True:
			await run.addTask()
		else:
			await run.removeTask()
	elif item == "web_preview":
		ads[ad_id][item] = True if ads[ad_id][item] == False else False
	elif item == "mode":
		ads[ad_id][item] = "send" if ads[ad_id][item] == "forward" else "forward"
	elif item == "sender":
		if ads[ad_id][item] == "bot" and config_dict['USER'] == "":
			await event.answer(text="User Session Not Added!", show_alert=True)
		else:
			ads[ad_id][item] = "bot" if ads[ad_id][item] == "user" else "user"
	elif item == "delete":
		adv = adVert(ad_id)
		adv.remove()
		if ad_id in tasks:
			task = adTaskHandler(ad_id)
			await task.removeTask()
		return await adword_conf(event, 'admenu', user)
	return await adword_setup(event, ad_id, user)


async def channel_conf(event, user, key, START=0):
	if key == "home":
		btns = ButtonMaker()
		btns.ibutton('♻️ 𝐔𝐏𝐃𝐀𝐓𝐄 ♻️', f'adword {user} update', position='header')
		btns.ibutton('🟩 𝐔𝐧𝐁𝐥𝐨𝐜𝐤 𝐀𝐥𝐥 🟩', f'adword {user} startall')
		btns.ibutton('🟥 𝐁𝐥𝐨𝐜𝐤 𝐀𝐥𝐥 🟥', f'adword {user} stopall')
		btns.ibutton('𝐁𝐀𝐂𝐊', f'adword {user} conf home')
		btns.ibutton('𝐂𝐋𝐎𝐒𝐄', f'adword {user} close')
		for k in list(OrderedDict(groups.items()).keys())[START:10+START]:
			btns.ibutton(f"{'🔴' if groups[k]['blocked'] else '🟢'} {groups[k].get('name')}", f"adword {user} chnl_set {k}")
		for x in range(0, len(groups)-1, 10):
			btns.ibutton(f'{int(x/10)+1}', f"adword {user} chnl_set page {x}", position='footer')
		return "", btns.build_menu(2)
	elif key == "update":
		user = config_dict['USER']
		if user == '':
			await event.answer(text="User Session Not Added!", show_alert=True)
		else:
			async for dialog in user.get_dialogs():
				if dialog.chat.type == ChatType.SUPERGROUP or dialog.chat.type == ChatType.GROUP:
					if dialog.chat.id not in groups:
						chat_id = await user.resolve_peer(dialog.chat.id)
						type = "supergroup" if dialog.chat.type == ChatType.SUPERGROUP else "group"
						state = hasattr(dialog.chat.permissions, "can_send_messages")
						
						groups[int(dialog.chat.id)] = {'name': dialog.chat.title,
												'blocked': False,
												'topic': [1],
												'web_preview': False,
												'type': "supergroup" if dialog.chat.type == ChatType.SUPERGROUP else "group",
												'msg_permission': dialog.chat.permissions.can_send_messages if state else dialog.chat.is_creator,
												'media_permission': dialog.chat.permissions.can_send_media_messages if state else dialog.chat.is_creator,
												'is_forum': False if type == "group" else (await user.invoke(GetChannels(id=[chat_id]))).chats[0].forum,
												'forums': {}
												}
						if groups[dialog.chat.id]['is_forum']:
							topics = await user.invoke(GetForumTopics(channel=chat_id, offset_date=0, offset_id=0, offset_topic=0, limit=1000))
							for topic in topics.topics:
								try:
									title = topic.title if topic.title else ''
									groups[dialog.chat.id]['forums'][topic.id] = {}
									groups[dialog.chat.id]['forums'][topic.id]['name'] = title
									groups[dialog.chat.id]['forums'][topic.id]['closed'] = topic.closed if topic.closed else ''
								except:
									pass
									
	elif key == "stopall" or key == "startall":
		for grp_id, group in groups.items():
			group['blocked'] = True if key == "stopall" else False
		return await channel_conf(event, user, "home")

async def channel_setup(event, chnl_id, user):
	btns = ButtonMaker()
	if chnl_id in groups:
		btns.ibutton("🔴 𝐁𝐥𝐨𝐜𝐤𝐞𝐝" if groups[chnl_id]['blocked'] else "🟢 𝐔𝐧𝐁𝐥𝐨𝐜𝐤𝐞𝐝", f'adword {user} chnl_set {chnl_id} block')
		if groups[chnl_id]['is_forum']:
			btns.ibutton(f"📩 𝐒𝐞𝐧𝐝 𝐓𝐨 𝐓𝐨𝐩𝐢𝐜 ⚙️", f'adword {user} chnl_set {chnl_id} topic')
	btns.ibutton('𝐁𝐀𝐂𝐊', f'adword {user} chnl_set', position='footer')
	btns.ibutton('𝐂𝐋𝐎𝐒𝐄', f'adword {user} close', position='footer')
	return "", btns.build_menu(1)


async def channel_settings(event, chnl_id, item, user):
	if item == "block":
		groups[chnl_id]['blocked'] = True if groups[chnl_id]['blocked'] == False else False
		return await channel_setup(event, chnl_id, user)
	elif item == "topic":
		btns = ButtonMaker()
		for id, topic in groups[chnl_id]['forums'].items():
			icon = "🟢" if id in groups[chnl_id]['topic'] else "🔴"
			btns.ibutton(f"{icon} {topic.get('name')}", f'adword {user} chnl_set {chnl_id} topic {id}')
		btns.ibutton('𝐁𝐀𝐂𝐊', f'adword {user} chnl_set {chnl_id}', position='footer')
		return "", btns.build_menu(2)


async def topic_settings(event, chnl_id, topic_id, user):
	groups[chnl_id]['topic'].remove(int(topic_id)) if int(topic_id) in groups[chnl_id]['topic'] else groups[chnl_id]['topic'].append(int(topic_id))
	return await channel_settings(event, chnl_id, "topic", user)
