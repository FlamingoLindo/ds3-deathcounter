import cv2 as cv
import numpy as np
import pytesseract
import difflib
import logging
import os

logger = logging.getLogger(__name__)

MIN_PIXELS = 50
MIN_FILL_RATIO = 0.005


def read_img():
    screenshots_dir = os.getenv("SCREENSHOTS_DIR", "screenshots")
    mask_path = os.path.join(screenshots_dir, "masked", "mask.png")

    mask = cv.imread(mask_path, cv.IMREAD_GRAYSCALE)
    if mask is None:
        return False

    h, w = mask.shape
    crop = mask[int(h * 0.40):int(h * 0.64), int(w * 0.28):int(w * 0.72)]

    if cv.countNonZero(crop) < MIN_PIXELS:
        return False

    kernel = np.ones((3, 3), np.uint8)
    crop = cv.morphologyEx(crop, cv.MORPH_CLOSE, kernel)

    if cv.countNonZero(crop) / crop.size < MIN_FILL_RATIO:
        return False

    ys, xs = np.nonzero(crop)
    box_w = xs.max() - xs.min() + 1
    box_h = ys.max() - ys.min() + 1
    if box_w < 40 or box_h < 10:
        return False

    crop = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    crop = cv.bitwise_not(crop)
    crop = cv.copyMakeBorder(crop, 20, 20, 20, 20,
                             cv.BORDER_CONSTANT, value=255)

    crop = cv.resize(crop, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

    try:
        text = pytesseract.image_to_string(
            crop,
            config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ ",
            timeout=5,
        )
    except (pytesseract.TesseractError, RuntimeError) as e:
        logger.warning("Tesseract failed on frame: %s", e)
        try:
            cv.imwrite(os.path.join(screenshots_dir, "bad_crop.png"), crop)
        except Exception:
            pass
        return False

    text = " ".join(text.upper().split())

    ratio = difflib.SequenceMatcher(
        None, text.replace(" ", ""), "YOUDIED").ratio()

    if text:
        logger.info("Text found on screen: %r", text)
    return ratio >= 0.70
