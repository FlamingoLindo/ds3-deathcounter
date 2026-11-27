import asyncio
import json
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator

from consts import APP_ID, APP_SECRET


async def first_login():
    with open("tokens.json", "w"):
        pass

    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, [])
    token, refresh = await auth.authenticate()

    with open("tokens.json", "w") as f:
        json.dump({"token": token, "refresh": refresh}, f)

if __name__ == "__main__":
    asyncio.run(first_login())
