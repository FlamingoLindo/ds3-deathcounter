import os
import queue
import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import state
import cv2
import numpy as np

from twitch.consts import TMP, FRAME

logger = logging.getLogger(__name__)


def run_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = "/opt/firefox/firefox"

    profile_dir = os.getenv("FIREFOX_PROFILE", "/data/firefox-profile")
    if os.path.isdir(profile_dir):
        options.add_argument("-profile")
        options.add_argument(profile_dir)

    os.makedirs(os.path.dirname(TMP), exist_ok=True)
    driver = None

    try:
        driver = webdriver.Firefox(options=options)
        logger.info('Starting selenium driver')

        # If you dont want the script to watch your own stream
        # you can chance `{state.channel_login}` to whatever streamer's username you want
        driver.get(
            f"https://player.twitch.tv/?channel={state.channel_login}&parent=twitch.tv")

        ok = driver.execute_script(
            "return MediaSource.isTypeSupported('video/mp4; codecs=\"avc1.64001f,mp4a.40.2\"')")
        logger.info("H.264 supported: %s", ok)

        try:
            btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-a-target="player-overlay-mature-accept"]')))
            btn.click()

            logger.info('Accepting mature content warning')
        except TimeoutException:
            logger.info('No mature content warning')

        while not state.stop.is_set():
            if not state.is_ds3.wait(timeout=1):
                continue

            driver.save_screenshot(TMP)
            os.replace(TMP, FRAME)

            png = driver.get_screenshot_as_png()
            img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
            try:
                state.frames.put_nowait(img)
            except queue.Full:
                pass
            time.sleep(0.5)
    except Exception:
        logger.exception("Selenium driver failed")
    finally:
        if driver is not None:
            logger.info('Closing driver')
            driver.quit()
