import json
import time
import random
import asyncio
import logging
import platform
import traceback
import configparser
from config import *
from pathlib import Path
from sqlite3 import OperationalError
from typing import List, Dict, Union

from telethon.sync import TelegramClient
from telethon import functions, types, events
from telethon.tl.types import Message
from telethon.tl.types import InputChannelEmpty

from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest

from telethon.errors import ReactionInvalidError, UserDeactivatedBanError

if platform.system() != 'Windows':
	import uvloop
	uvloop.install()

WORK_DIR.mkdir(exist_ok=True)

loggers = ['info', 'error']
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')

apps = []
sent = []

for logger_name in loggers:
	logger = logging.getLogger(logger_name)
	logger.setLevel(logging.INFO)
	log_filepath = LOGS_DIR.joinpath(f'{logger_name}.log')
	handler = logging.FileHandler(log_filepath)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.warning('Start reaction bot.')

error = logging.getLogger('error')
info = logging.getLogger('info')

async def send_reaction(client: TelegramClient, message: Message, config_dict) -> None:
	"""Handler for sending reactions"""
	emoji = random.choice(EMOJIS)
	app_name = config_dict['name']
	try:
		random_sleep_time = random.randint(1, 5)
		await asyncio.sleep(random_sleep_time)
		reaction = [types.ReactionEmoji(emoticon=emoji)]
		await client(SendReactionRequest(
			peer=message.chat_id,
			msg_id=message.id,
			big=True,
			add_to_recent=True,
			reaction=reaction
		))
		print(f'Session {app_name} sent - {emoji}')
	except ReactionInvalidError:
		print(f'{emoji} - invalid reaction')
	except UserDeactivatedBanError:
		print(f'Session banned - {app_name}')
	except Exception as e:
		pass
		#error.warning(traceback.format_exc())
		#print(traceback.format_exc())

async def send_reaction_from_all_applications(event: events.NewMessage.Event) -> None:
	"""
	What is it for? Why not just assign a handler function to each app?

	The answer is simple, if several sessions have the same API_ID and API_HASH,
	only one of those sessions will send a response!
	"""
	post = (event.chat_id, event.id)

	if post in sent:
		return
	
	sent.append(post)

	for app, config_dict, _ in apps:
		await send_reaction(app, event, config_dict)

async def get_chat_id(app: TelegramClient, chat_link: str) -> Union[int, str, None]:
	"""Return chat_id or None or raise AttributeError"""
	result = await app(CheckChatInviteRequest(chat_link))
	try:
		chat = await app.get_entity(result.chat.id)
		#print(chat.id)
	except Exception as e:
		error.warning(traceback.format_exc())
		return None
	else:
		return chat.id

async def get_config_files_path() -> List[Path]:
	"""Take all the configuration files"""
	return [str(file.resolve()) for file in WORK_DIR.iterdir() if file.suffix.lower() in CONFIG_FILE_SUFFIXES]

async def config_from_ini_file(file_path: Path) -> Dict:
	"""Pull the config from the *.ini file"""
	config_parser = configparser.ConfigParser()
	config_parser.read(file_path)
	section = config_parser.sections()[0]
	return {**config_parser[section]}

async def get_config(file_path: str) -> Dict:
	"""Return the config file to the path"""
	file_path = Path(file_path)  # Convert the string to a Path object
	config_suffixes = {
		'.ini': config_from_ini_file,
	}
	suffix = file_path.suffix.lower()
	config = await config_suffixes[suffix](file_path)
	normalized_config = {'name': file_path.stem}
	for key, values in POSSIBLE_KEY_NAMES.items():
		for value in values:
			if not config.get(value):
				continue
			normalized_config[key] = config[value]
			break
	return normalized_config

async def create_apps(config_files_paths: List[Path]) -> None:
	"""
	Create 'Client' instances from config files.
	**If there is no name key in the config file, then the config file has the same name as the session!**
	"""
	for config_file_path in config_files_paths:
		try:
			config_file_path = Path(config_file_path)
			config_dict = await get_config(config_file_path)
			bot_name = config_dict['name']
			api_id = config_dict['api_id']
			api_hash = config_dict['api_hash']
			phone_number = config_dict['phone_number']
			session_file_path = WORK_DIR.joinpath(config_file_path.with_suffix('.session'))
			apps.append((TelegramClient(str(session_file_path), api_id, api_hash), config_dict, session_file_path))
		except Exception as e:
			pass
			#error.warning(traceback.format_exc())
			#error.warning(traceback.format_exc())

async def join_channel(client: TelegramClient, invite_link: str):
	"""Join a channel (public or private)"""
	try:
		await client(ImportChatInviteRequest(invite_link))
		error.warning(f"Successfully joined the channel with invite link: {invite_link}")
	except Exception as e:
		print(f"Failed to join the channel with invite link: {invite_link}")
		print(f"Reason: {str(e)}")
		#error.warning(traceback.format_exc())

async def is_subscribed(app: TelegramClient, chat_link: str) -> bool:
	"""Check if the channel is subscribed"""
	join = await join_channel(app, chat_link)
	try:
		chat_id = await get_chat_id(app, chat_link)

		if chat_id is None:
			return False

		return True
	except Exception as e:
		error.warning(traceback.format_exc())
		return False
	else:
		return True

@events.register(events.NewMessage)
async def message_handler(event):
	await send_reaction_from_all_applications(event)

async def main():
	"""
	Main function:
		- Create a directory of sessions if not created.
		- Take all config files (*.json, *.ini)
		- Create clients by their config files.
		- Run through clients, add handler, start and join chat
		- Wait for completion and finish (infinitely)
	"""
	config_files = await get_config_files_path()

	await create_apps(config_files)
	if not apps:
		print('No Session Files!')
		raise Exception('No Session Files!')

	for app, config_dict, session_file_path in apps:
		print(config_dict)
		app_name = config_dict['name']
		app_id = config_dict['api_id']
		api_hash = config_dict['api_hash']
		phone_number = config_dict['phone_number']

		try:
			await app.start()
		except Exception as e:
			error.warning(traceback.format_exc())
			apps.remove((app, config_dict, session_file_path))
			error.warning(traceback.format_exc())
			continue

		app.add_event_handler(message_handler)

		print(f'Session started - {app_name}')
		info.info(f'Session started - {app_name}')
		for channel in CHANNELS_LIST:
			subscribed = await is_subscribed(app, channel)
			if not subscribed:
				random_sleep_time = random.randint(1, 10)
				await asyncio.sleep(random_sleep_time)
				await join_channel(app, channel)

	info.warning('All sessions started!')

	for app, config_dict, _ in apps:
		app_name = config_dict['name']
		try:
			info.warning(f'Stopped - {app_name}')
			await app.run_until_disconnected()
		except ConnectionError as e:
			error.warning(traceback.format_exc())
			pass

	apps[:] = []

def start():
	"""Let's start"""
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(main())
	except Exception as e:
		error.warning(traceback.format_exc())
		error.critical(traceback.format_exc())
		error.warning(f'Waiting {TRY_AGAIN_SLEEP} sec. before restarting the program...')
		time.sleep(TRY_AGAIN_SLEEP)

if __name__ == '__main__':
	print("Let's start...")
	while True:
		start()