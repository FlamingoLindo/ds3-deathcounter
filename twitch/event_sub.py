import json
import os
import logging
import asyncio
from twitchAPI.twitch import Twitch
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelUpdateEvent

from twitch.driver import run_driver, state
from twitch.consts import GAME_NAME, BROADCASTER_ID, APP_ID, APP_SECRET
from reader.reader import run_reader

logger = logging.getLogger(__name__)

TOKEN_FILE = os.getenv("TOKEN_FILE", "/data/tokens/tokens.json")


async def save_tokens(token: str, refresh: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token, "refresh": refresh}, f)


async def wait_for_ds3(data: ChannelUpdateEvent):
    state.stream_title = data.event.title
    if data.event.category_name == GAME_NAME:
        state.is_ds3.set()
        logger.info('Started streaming Dark Sous 3')
    else:
        state.is_ds3.clear()
        logger.info('Stopped streaming Dark Sous 3')


async def start_twitch():
    logger.info('Starting twitch auth process')

    with open(TOKEN_FILE) as f:
        saved = json.load(f)

    twitch = await Twitch(APP_ID, APP_SECRET)
    twitch.user_auth_refresh_callback = save_tokens
    await twitch.set_user_authentication(saved["token"], [], saved["refresh"])

    logger.info('Authentication completed')

    info = await twitch.get_channel_information(BROADCASTER_ID)

    if isinstance(info, list):
        info = info[0] if info else None
    if info and info.game_name == GAME_NAME:
        state.is_ds3.set()

        logger.info('Dark Souls 3 already running')

    state.channel_login = info.broadcaster_login
    state.stream_title = info.title

    eventsub = EventSubWebsocket(twitch)
    eventsub.start()
    await eventsub.listen_channel_update_v2(BROADCASTER_ID, wait_for_ds3)

    driver_task = asyncio.create_task(asyncio.to_thread(run_driver))
    reader_task = asyncio.create_task(asyncio.to_thread(run_reader))

    try:
        await asyncio.Event().wait()
    finally:
        state.stop.set()
        await eventsub.stop()
        await twitch.close()
        await asyncio.gather(driver_task, reader_task)
