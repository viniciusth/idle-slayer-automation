from collections import namedtuple
from idle_slayer_automation.image_processing.searcher import ScreenshotSearcher


def test_image_search_and_casting():
    byte_string = open("tests/screenshot.bytes", "rb").read()
    ScreenshotMock = namedtuple("Screenshot", ["bgra", "height", "width"])
    screenshot = ScreenshotMock(byte_string, 759, 1296)

    searcher = ScreenshotSearcher()

    matches = searcher.search_screenshot(screenshot)
    assert len(matches) == 1, f"Expected 1 match, got {matches}"
    match = matches[0]
    assert (
        match["sprite"] == "silver_box"
    ), f"Expected silver_box, got {match['sprite']}"
