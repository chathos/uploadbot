#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# the secret configuration specific things
from config.sample import Config
# the Strings used for this "thing"
from translation import Translation

import getpass
from telethon import TelegramClient, events
from telethon.errors import (
    RPCError, BrokenAuthKeyError, ServerError,
    FloodWaitError, FloodTestPhoneWaitError, FileMigrateError,
    TypeNotFoundError, UnauthorizedError, PhoneMigrateError,
    NetworkMigrateError, UserMigrateError, SessionPasswordNeededError
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.utils import get_display_name

import os
# https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un
import requests
import re

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    content_length = int(header.get('content-length', None))
    if content_length and content_length > Config.MAX_FILE_SIZE:  # 200 mb approx
        return False
    return True


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def progress_response_callback_handler(current, total):
    print("Percent: " + str((current / total) * 100))


def DownLoadFile(url, file_name):
    if not os.path.exists(file_name):
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
                fd.write(chunk)
    return file_name

def process_update(update):
    if update.message.from_id in Config.AUTHORIZED_USERS:
        if update.message.media is not None:
            media_message = update.message.media
            directory_name = Config.DOWNLOAD_LOCATION
            m1 = client.send_message(update.message.from_id, "Requesting download ... Please be patient")
            downloaded_file_location = client.download_media(media_message, directory_name, progress_response_callback_handler)
            client.edit_message(update.message.from_id, m1, "Downloaded Successfully. " + str(Config.EXAMPLE_WEB_DOMAIN) + "/" + str(downloaded_file_location) + "")
        else:
            if update.message.message.startswith("http"):
                received_id = update.message.from_id
                received_message = update.message.message
                url = ""
                file_name = ""
                if Translation.URL_FILE_SEPERATOR in received_message:
                    url, file_name = received_message.split(Translation.URL_FILE_SEPERATOR)
                else:
                    url = received_message
                    # get file name from Content Disposition
                    r = requests.head(url, allow_redirects=True)
                    file_name = get_filename_from_cd(r.headers.get('content-disposition'))
                    # the above thing NEVER works, FallBack:
                    if file_name is None:
                        file_name = url.split("/")[-1]
                # received the `url` and `file_name` here! Do something magical with it!
                if is_downloadable(url):
                    m1 = client.send_message(received_id, "Trying to download provided Link")
                    # download file_name to Config.DOWNLOAD_LOCATION
                    t = DownLoadFile(url, Config.DOWNLOAD_LOCATION + "/" + file_name)
                    client.edit_message(received_id, m1.id, "Downloaded. Trying to upload to Telegram")
                    # upload file to Telegram
                    client.send_file(received_id, t, caption=Translation.STOP_TEXT, force_document=True, progress_callback=progress_response_callback_handler, allow_cache=False)
                    # It worked!
                    os.remove(t)
                    client.edit_message(received_id, m1.id, Translation.STOP_TEXT)
                else:
                    client.send_message(update.message.from_id, Translation.FREE_USER_LIMIT)
            else:
                m3 = client.send_message(update.message.from_id, Translation.START_TEXT)
    else:
        client.send_message(update.message.from_id, Translation.STILL_NOT_HANDLED_MSG)

if __name__ == "__main__":
    client = TelegramClient(
        Config.TL_SESSION,
        Config.APP_ID,
        Config.API_HASH,
        update_workers = 4,
        spawn_read_thread = False
    )
    client.connect()
    if not client.is_user_authorized():
        # https://github.com/LonamiWebs/Telethon/issues/36#issuecomment-287735063
        client.sign_in(bot_token=Config.TG_BOT_TOKEN)
    me = client.get_me()
    logger.info(me.stringify())
    if not os.path.exists(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    client.add_event_handler(process_update)
    client.idle()  # ends with Ctrl+C
