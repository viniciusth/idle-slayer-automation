import pygetwindow as gw
import mss, mss.tools
import time
import multiprocessing as mp

from .searcher import ScreenshotSearcher
from .rect import get_window_rect


def startup(info_msgs: mp.Queue, eye_msgs: mp.Queue):
    window: gw.Win32Window = gw.getWindowsWithTitle("Idle Slayer")[0]
    if window is None:
        raise Exception("Idle Slayer window not found")
    window.restore()
    window.activate()

    amount = 0
    start = time.time()
    info_toggled = False

    searcher = ScreenshotSearcher()

    with mss.mss() as sct:
        while True:
            rect = get_window_rect(window._hWnd)
            sct_img = sct.grab(
                (
                    rect.left,
                    rect.top,
                    rect.left + rect.width,
                    rect.top + rect.height,
                )
            )
            if not info_msgs.empty():
                info_msgs.get()
                info_toggled = not info_toggled

            matches = searcher.search_screenshot(sct_img)

            amount += 1
            if time.time() - start > 1:
                if info_toggled:
                    print(f"FPS: {amount}, current_matches = {matches}")
                amount = 0
                start = time.time()
