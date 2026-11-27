"""_summary_
    """
import os
import logging
import asyncio
from twitch.event_sub import start_twitch

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(
        filename=os.getenv("LOG_FILE", "logs.log"),
        level=logging.INFO,
    )
    try:
        asyncio.run(start_twitch())
    except KeyboardInterrupt:
        pass
