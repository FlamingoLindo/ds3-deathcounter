"""_summary_

    Raises:
        FileNotFoundError: _description_
    """

import os
import cv2 as cv
import numpy as np
import logging

logger = logging.getLogger(__name__)


def create_mask(img):
    image = img

    height, width = image.shape[:2]
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    h, s, v = cv.split(hsv)
    reddish = ((h <= 10) | (h >= 170)) & (s > 50)

    # print("reddish pixels:", np.count_nonzero(reddish))
    # logger.info('Reddish pixels: %s', np.count_nonzero(reddish))

    if reddish.any():
        lower_s = int(np.percentile(s[reddish], 5))
        lower_v = int(np.percentile(v[reddish], 5))
    else:
        lower_s, lower_v = 100, 40

    mask1 = cv.inRange(hsv, (170, lower_s, lower_v), (180, 255, 255))
    mask2 = cv.inRange(hsv, (0, lower_s, lower_v), (10, 255, 255))
    mask = mask1 | mask2

    masked_dir = os.path.join(
        os.getenv("SCREENSHOTS_DIR", "screenshots"), "masked")
    os.makedirs(masked_dir, exist_ok=True)
    # cv.imwrite(os.path.join(masked_dir, "mask.png"), mask)
    tmp_path = os.path.join(masked_dir, "mask.tmp.png")
    cv.imwrite(tmp_path, mask)
    os.replace(tmp_path, os.path.join(masked_dir, "mask.png"))

    # print(f"{cv.countNonZero(mask) / (width * height):.2%}")
