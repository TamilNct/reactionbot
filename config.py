import os
from pathlib import Path

CHANNELS_LIST = ['4XZhZqXpo6Q1NDg1']
CHANNEL_IDS = ['-1002112202931']

POSSIBLE_KEY_NAMES = {
    'api_id': ['api_id', 'app_id'],
    'api_hash': ['api_hash', 'app_hash'],
    'phone_number': ['phone_number', 'phone']
}

TRY_AGAIN_SLEEP = 20

BASE_DIR = Path(__file__).parent
WORK_DIR = BASE_DIR.joinpath('sessions')
LOGS_DIR = BASE_DIR.joinpath('logs')

CONFIG_FILE_SUFFIXES = '.ini'

EMOJIS = ['👍', '❤️', '🔥', '🥰', '👏', '🎉', '🤩', '⚡️', '💯']