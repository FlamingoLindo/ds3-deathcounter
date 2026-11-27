import os
import queue
from datetime import datetime
import cv2
import state
from utils.configs import Configs
from reader.create_mask import create_mask
from reader.read_img import read_img
from db.add_death_dto import AddDeathDTO
import logging

import time

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 10


def run_reader():
    db = Configs.start_up()
    last_death = None
    frames_seen = 0
    # last_beat = time.monotonic()

    while not state.stop.is_set():
        # if time.monotonic() - last_beat > 30:
        #     logger.info("Reader alive: %d frames processed", frames_seen)
        #     last_beat = time.monotonic()

        try:
            img = state.frames.get(timeout=1)
        except queue.Empty:
            continue

        try:
            frames_seen += 1
            create_mask(img)
            found = read_img()

            now = datetime.now()
            if found and (last_death is None or
                          (now - last_death).total_seconds() > COOLDOWN_SECONDS):

                last_death = now

                db.add_death(AddDeathDTO(
                    stream_title=state.stream_title,
                    timestamp=now.isoformat(timespec="seconds"),
                ))

                death_number = db.count_deaths()

                deaths_dir = os.path.join(
                    os.getenv("SCREENSHOTS_DIR", "screenshots"), "deaths")

                os.makedirs(deaths_dir, exist_ok=True)

                if not cv2.imwrite(os.path.join(deaths_dir, f"{death_number}.png"), img):
                    logger.error('Failed to save screenshot')

                # logger.info('Current death count: %s', death_number)
        except Exception:
            logger.exception("Reader failed on a frame, continuing")
