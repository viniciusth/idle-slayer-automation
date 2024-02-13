from collections import namedtuple
from idle_slayer_automation.image_processing.searcher import ScreenshotSearcher, Sprite
import os


def test_image_search_and_casting():
    byte_string = open("tests/screenshot.bytes", "rb").read()
    ScreenshotMock = namedtuple("Screenshot", ["bgra", "height", "width"])
    screenshot = ScreenshotMock(byte_string, 759, 1296)

    searcher = ScreenshotSearcher()

    matches = searcher.search_screenshot(screenshot)
    assert len(matches) == 1, f"Expected 1 match, got {matches}"
    match = matches[0]
    assert (
        match["sprite"] == Sprite.SILVER_BOX
    ), f"Expected silver_box, got {match['sprite']}"

    if os.getenv("SHOW_IMAGES") == "1":
        import cv2

        img = ScreenshotSearcher.cast_screenshot(screenshot)
        rect = match["rect"]
        cv2.rectangle(
            img,
            (rect.left, rect.top),
            (rect.right, rect.bottom),
            (0, 255, 0),
            2,
        )
        cv2.imshow("screenshot", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
