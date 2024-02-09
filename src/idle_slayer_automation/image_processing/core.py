import pygetwindow as gw
import mss, mss.tools
import time
import multiprocessing as mp
from .overlay import OverlayHandler, WindowRect


def startup(info_msgs: mp.Queue, eye_msgs: mp.Queue):
    window: gw.Win32Window = gw.getWindowsWithTitle("Idle Slayer")[0]
    if window is None:
        raise Exception("Idle Slayer window not found")
    window.restore()
    window.activate()
    print("Window found, rect:", window.left, window.top, window.width, window.height)
    amount = 0
    start = time.time()
    overlay = OverlayHandler(window._hWnd)
    info_toggled = False
    while True:
        with mss.mss() as sct:
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

        amount += 1
        if time.time() - start > 1:
            if info_toggled:
                overlay.draw_fps(amount)
                overlay.draw_rect_outline(WindowRect(50, 50, 100, 100, 50, 50))
            amount = 0
            start = time.time()
