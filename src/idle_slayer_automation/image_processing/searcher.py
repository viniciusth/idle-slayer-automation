from mss.screenshot import ScreenShot
from typing import List, TypedDict
import numpy as np
import cv2

from idle_slayer_automation.image_processing.overlay import WindowRect

SPRITES = ["chest", "offline_extra", "saver", "silver_box", "silver_boxes"]
SPRITE_PATHS = [f"sprites/{sprite}.png" for sprite in SPRITES]


class SearchResult(TypedDict):
    sprite: str
    rect: WindowRect


class ScreenshotSearcher:
    def __init__(self):
        self.sift = cv2.SIFT_create()

        self.imgs = [cv2.imread(sprite_path) for sprite_path in SPRITE_PATHS]
        self.sifts = [self.sift.detectAndCompute(img, None) for img in self.imgs]
        self.bf = cv2.BFMatcher(cv2.NORM_L2SQR, crossCheck=True)

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
        results = []
        kp1, des1 = self.sift.detectAndCompute(img, None)

        for i, (_, des2) in enumerate(self.sifts):
            matches = self.bf.match(des1, des2)
            match = min(matches, key=lambda x: x.distance)

            if match.distance < 8000:
                pts = np.int32(kp1[match.queryIdx].pt)

                results.append(
                    {
                        "sprite": SPRITES[i],
                        "rect": WindowRect(
                            pts[0] - 10, pts[1] - 10, pts[0] + 10, pts[1] + 10
                        ),
                    }
                )
        return results
