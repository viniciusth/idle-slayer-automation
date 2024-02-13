from mss.screenshot import ScreenShot
from typing import List, TypedDict
import numpy as np
import cv2
import multiprocessing as mp

from idle_slayer_automation.image_processing.rect import WindowRect

SPRITES = ["chest", "offline_extra", "saver", "silver_box", "silver_boxes"]
SPRITE_PATHS = [f"sprites/{sprite}.png" for sprite in SPRITES]


class SearchResult(TypedDict):
    sprite: str
    rect: WindowRect
    certainty: float


def search_template(i, img, template) -> SearchResult | None:
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.argmax(res)
    (x, y) = np.unravel_index(loc, res.shape)
    return (
        {
            "sprite": SPRITES[i],
            "rect": WindowRect(x, y, x + template.shape[1], y + template.shape[0]),
            "certainty": res[x, y],
        }
        if res[x, y] > threshold
        else None
    )


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
