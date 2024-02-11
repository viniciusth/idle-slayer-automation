import pygetwindow as gw
import mss, mss.tools
import time
import multiprocessing as mp
from .overlay import OverlayHandler, get_window_rect


def startup(info_msgs: mp.Queue, eye_msgs: mp.Queue):
    window: gw.Win32Window = gw.getWindowsWithTitle("Idle Slayer")[0]
    if window is None:
        raise Exception("Idle Slayer window not found")
    window.restore()
    window.activate()
    amount = 0
    start = time.time()
    overlay = OverlayHandler(window._hWnd)
    info_toggled = False
    with mss.mss() as sct:
        while True:
            window_rect = get_window_rect(window._hWnd)
            sct_img = sct.grab(
                (
                    window.left,
                    window.top,
                    window.left + window.width,
                    window.top + window.height,
                )
            )

            if not info_msgs.empty():
                info_msgs.get()
                info_toggled = not info_toggled
                if not info_toggled:
                    overlay.clear()

            if info_toggled:
                pass

            amount += 1
            if time.time() - start > 1:
                if info_toggled:
                    overlay.draw_fps(amount)
                amount = 0
                start = time.time()
