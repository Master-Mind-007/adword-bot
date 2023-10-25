#!/usr/bin/env python3

######################################################
# AUTHOR: MIKHIL
# TELEGRAM: @MASTERMIND_MIKHIL @MASTERMIKHIL
# PROJECT: ADWORD
# DISTRIBUTION IS PROHIBITED WITHOUT PREMISSION
######################################################

from pyrogram.filters import command, regex
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from worker import user_data, bot, user, config_dict, ads
from worker.helper.telegram_helper.message_utils import sendMessage, editMessage, deleteMessage, editReplyMarkup
from worker.helper.telegram_helper.filters import CustomFilters
from worker.helper.telegram_helper.bot_commands import BotCommands
from worker.helper.telegram_helper.button_build import ButtonMaker
from worker.helper.ext_utils.bot_utils import update_user_ldata, new_task
from worker.helper.ext_utils.adwords import adword_conf, adword_setup, adword_settings, channel_conf, channel_setup, channel_settings, topic_settings, groups


async def adword(client, message):
	user_id = message.from_user.id
	msg, btn = await adword_conf(message, 'home', user_id)
	await sendMessage(message, msg, btn, config_dict['COVER_IMAGE'])


@new_task
async def adwordx(_, query):
	message = query.message
	user_id = query.from_user.id
	data = query.data.split()
	if user_id != int(data[1]):
		return await query.answer(text="Not Yours!", show_alert=True)
	elif len(data) == 3:
		if data[2] == "close":
			await query.answer()
			await deleteMessage(message)
			if message.reply_to_message:
				await deleteMessage(message.reply_to_message)
				if message.reply_to_message.reply_to_message:
					await deleteMessage(message.reply_to_message.reply_to_message)
		elif data[2] == "admenu":
			msg, btn = await adword_conf(query, data[2], data[1])
			await editReplyMarkup(message, btn)
		elif data[2] == "chnl_set":
			if config_dict['USER'] == '':
				await query.answer(text="User Session Not Added!", show_alert=True)
			else:
				msg, btn = await channel_conf(query, data[1], "home")
				await editReplyMarkup(message, btn)
		elif data[2] == "update":
			msg = "<i><b>Loading Channels...</i></b>"
			await editMessage(message, msg, photo=config_dict['COVER_IMAGE'])
			await channel_conf(query, data[1], "update")
			msg, btn = await channel_conf(query, data[1], "home")
			await editMessage(message, "", photo=config_dict['COVER_IMAGE'])
			await editReplyMarkup(message, btn)
		elif data[2] == "stopall" or data[2] == "startall":
			msg, btn = await channel_conf(query, data[1], data[2])
			await editReplyMarkup(message, btn)
		elif data[2] == "conf":
			msg, btn = await adword_conf(query, "conf", data[1])
			await editReplyMarkup(message, btn)
	elif len(data) == 4:
		if data[2] == "conf":
			if data[3] == "enableall" and config_dict['USER'] == '':
				return await query.answer(text="User Session Not Added!", show_alert=True)
			elif data[3] == "enableall" and len(groups) == 0:
				return await query.answer(text="No Groups Found!\nTry Updating Groups from Groups Settings!", show_alert=True)
			else:
				msg, btn = await adword_conf(query, data[3], data[1])
				await editReplyMarkup(message, btn)
		if data[2] == "chnl_set":
			msg, btn = await channel_setup(query, int(data[3]), data[1])
			await editReplyMarkup(message, btn)
	elif len(data) == 5:
		if data[2] == "conf":
			msg, btn = await adword_setup(query, data[4], data[1])
			await editMessage(message, msg, btn, config_dict['COVER_IMAGE'])
		elif data[2] == "chnl_set":
			if data[3] == "page":
				msg, btn = await channel_conf(query, data[1], "home", int(data[4]))
				await editReplyMarkup(message, btn)
			else:
				msg, btn = await channel_settings(query, int(data[3]), data[4], data[1])
				await editReplyMarkup(message, btn)
	elif len(data) == 6:
		if data[2] == "conf":
			if data[4] == "page":
				msg, btn = await adword_conf(query, data[3], data[1], int(data[5]))
				await editReplyMarkup(message, btn)
			else:
				if data[5] == "enabled" and config_dict['USER'] == '':
					return await query.answer(text="User Session Not Added!", show_alert=True)
				elif data[5] == "enabled" and len(groups) == 0:
					return await query.answer(text="No Groups Found!\nTry Updating Groups from Groups Settings!", show_alert=True)
				elif data[5] == "enabled" and ads[data[3]]['msg'] == '':
					return await query.answer(text="Empty Advertisement!", show_alert=True)
				else:
					msg, btn = await adword_settings(query, data[3], data[5], data[1])
					await editMessage(message, msg, btn, config_dict['COVER_IMAGE'])
		elif data[2] == "chnl_set":
			msg, btn = await topic_settings(query, int(data[3]), data[5], data[1])
			await editReplyMarkup(message, btn)


bot.add_handler(MessageHandler(adword, filters=command(
	BotCommands.AdwordCommand) & CustomFilters.authorized & ~CustomFilters.blacklisted))
bot.add_handler(CallbackQueryHandler(adwordx,
				filters=regex("^adword")))
