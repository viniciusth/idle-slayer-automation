from mss.screenshot import ScreenShot
from typing import List, TypedDict
import numpy as np
import cv2
import multiprocessing as mp
from enum import Enum

from idle_slayer_automation.image_processing.rect import WindowRect


class Sprite(Enum):
    CHEST = "chest"
    OFFLINE_EXTRA = "offline_extra"
    SAVER = "saver"
    SILVER_BOX = "silver_box"
    SILVER_BOXES = "silver_boxes"
    BOX = "box"
    CLOSE_CHEST_HUNT = "close_chest_hunt"
    BONUS_STAGE = "bonus_stage"
    START_BONUS = "start_bonus"
    START_BONUS_2 = "start_bonus_2"
    SECOND_WIND = "second_wind"


SPRITES = [sprite.value for sprite in Sprite]
SPRITE_PATHS = [f"sprites/{sprite}.png" for sprite in SPRITES]


class SearchResult(TypedDict):
    sprite: Sprite
    rect: WindowRect
    certainty: float


def search_template(i, img, template) -> SearchResult | None:
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.argmax(res)
    (x, y) = np.unravel_index(loc, res.shape)
    return (
        {
            "sprite": Sprite(SPRITES[i]),
            "rect": WindowRect(y, x, x + template.shape[0], y + template.shape[1]),
            "certainty": res[x, y],
        }
        if res[x, y] > threshold
        else None
    )


# TODO: we can improve performance by identifying what stage we are in and only searching for the relevant sprites


class ScreenshotSearcher:
    def __init__(self):
        self.imgs = [cv2.imread(sprite_path) for sprite_path in SPRITE_PATHS]
        self.pool = mp.Pool(processes=4)

    def cast_screenshot(screenshot: ScreenShot) -> np.ndarray:
        """
        Casts a mss screenshot into a numpy array.

        Transforms raw bytes into array, reshape into matrix with 4 channels, remove alpha channel.
        """
        return (
            np.frombuffer(screenshot.bgra, dtype=np.uint8)
            .reshape((screenshot.height, screenshot.width, 4))[:, :, :3]
            .copy()
        )

    def search_screenshot(self, screenshot: ScreenShot) -> List[SearchResult]:
        """
        Searches for a template in a screenshot.
        """
        img = ScreenshotSearcher.cast_screenshot(screenshot)

        results = self.pool.starmap(
            search_template, [(i, img, self.imgs[i]) for i in range(len(self.imgs))]
        )
        results = [result for result in results if result is not None]

        return results
