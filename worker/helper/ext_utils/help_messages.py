#!/usr/bin/env python3
from worker.helper.telegram_helper.bot_commands import BotCommands

help_string = [f'''<b><i>𝐁𝐚𝐬𝐢𝐜 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬!</i></b>

<b>Use Adword Command to add your Advertisement for listing.</b>
┠ /{BotCommands.AdwordCommand[0]} or /{BotCommands.AdwordCommand[1]}: Add Advertisement.
''',

f'''<b><i>𝐔𝐬𝐞𝐫𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬!</i></b>

<b>Bot Stats:</b>
┠ /{BotCommands.StatsCommand[0]} or /{BotCommands.StatsCommand[1]}: Show Server detailed stats.
┖ /{BotCommands.PingCommand[0]} or /{BotCommands.PingCommand[1]}: Check how long it takes to Ping the Bot.
''',

f'''<b><i>𝐎𝐰𝐧𝐞𝐫 𝐨𝐫 𝐒𝐮𝐝𝐨𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬!</i></b>

<b>Bot Settings:</b>
┠ /{BotCommands.BotSetCommand[0]} or /{BotCommands.BotSetCommand[1]} [query]: Open Bot Settings (Only Owner & Sudo).

<b>Authentication:</b>
┠ /{BotCommands.AuthorizeCommand[0]} or /{BotCommands.AuthorizeCommand[1]}: Authorize a chat or a user to use the bot (Only Owner & Sudo).
┠ /{BotCommands.UnAuthorizeCommand[0]} or /{BotCommands.UnAuthorizeCommand[1]}: Unauthorize a chat or a user to use the bot (Only Owner & Sudo).
┠ /{BotCommands.AddSudoCommand}: Add sudo user (Only Owner).
┠ /{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner).
┠ /{BotCommands.AddBlackListCommand[0]} or /{BotCommands.AddBlackListCommand[1]}: Add User in BlackListed, so that user can't use the Bot anymore.
┖ /{BotCommands.RmBlackListCommand[0]} or /{BotCommands.RmBlackListCommand[1]}: Remove a BlackListed User, so that user can again use the Bot.

<b>Maintainance:</b>
┠ /{BotCommands.RestartCommand[0]} or /{BotCommands.RestartCommand[1]}: Restart and Update the Bot (Only Owner & Sudo).
┠ /{BotCommands.RestartCommand[2]}: Restart and Update all Bots (Only Owner & Sudo).
┖ /{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).

<b>Executors:</b>
┠ /{BotCommands.ShellCommand}: Run shell commands (Only Owner).
┠ /{BotCommands.EvalCommand}: Run Python Code Line | Lines (Only Owner).
┠ /{BotCommands.ExecCommand}: Run Commands In Exec (Only Owner).
┠ /{BotCommands.ClearLocalsCommand}: Clear {BotCommands.EvalCommand} or {BotCommands.ExecCommand} locals (Only Owner).
┖ /exportsession: Generate User StringSession of Same Pyro Version (Only Owner).
''',

f'''<b><i>𝐌𝐢𝐬𝐜𝐞𝐥𝐥𝐚𝐧𝐞𝐨𝐮𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬!</i></b>

<b>Extras:</b>
┠ /{BotCommands.SpeedCommand[0]} or /{BotCommands.SpeedCommand[1]}: Check Speed in VPS/Server.
''']

default_desp = {'AS_DOCUMENT': 'Default type of Telegram file upload. Default is False mean as media.',
                'AUTHORIZED_CHATS': 'Fill user_id and chat_id of groups/users you want to authorize. Separate them by space.',
                'BASE_URL': 'Valid BASE URL where the bot is deployed to use torrent web files selection. Format of URL should be http://myip, where myip is the IP/Domain(public) of your bot or if you have chosen port other than 80 so write it in this format http://myip:port (http and not https). Str',
                'BASE_URL_PORT': 'Which is the BASE_URL Port. Default is 80. Int',
                'FSUB_IDS': 'Fill chat_id(-100xxxxxx) of groups/channel you want to force subscribe. Separate them by space. Int\n\nNote: Bot should be added in the filled chat_id as admin',
                'BOT_PM': 'File/links send to the BOT PM also. Default is False',
                'BOT_TOKEN': 'The Telegram Bot Token that you got from @BotFather',
                'CMD_SUFFIX': 'commands index number. This number will added at the end all commands.',
                'DOWNLOAD_DIR': 'The path to the local folder where the downloads should be downloaded to. ',
                'SUDO_USERS': 'Fill user_id of users whom you want to give sudo permission. Separate them by space. Int',
                'TELEGRAM_API': 'This is to authenticate your Telegram account for downloading Telegram files. You can get this from https://my.telegram.org.',
                'TELEGRAM_HASH': 'This is to authenticate your Telegram account for downloading Telegram files. You can get this from https://my.telegram.org.',
                'TIMEZONE': 'Set your Preferred Time Zone for Restart Message. Get yours at <a href="http://www.timezoneconverter.com/cgi-bin/findzone.tzc">Here</a> Str',
                'SET_COMMANDS': 'Set bot command automatically. Bool',
                'USER_SESSION_STRING': "Set User Session String to Send Messages in Groups.\nUse <code>/exportsession</code> command to Generate Session String.",
                }
