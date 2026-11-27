import os
from dotenv import load_dotenv

load_dotenv()

GAME_NAME = "DARK SOULS III"
SCREENSHOT_PATH = os.path.join(
    os.getenv("SCREENSHOTS_DIR", "screenshots"), ".temp")

APP_ID = os.environ["APP_ID"]
APP_SECRET = os.environ["APP_SECRET"]
BROADCASTER_ID = os.environ["BROADCASTER_ID"]

FRAME = os.path.join(SCREENSHOT_PATH, "finding_death.png")
TMP = os.path.join(SCREENSHOT_PATH, "finding_death.tmp.png")
