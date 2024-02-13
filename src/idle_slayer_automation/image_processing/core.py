from multiprocessing.connection import PipeConnection
from typing import List
import pygetwindow as gw
import mss, mss.tools
import time
import multiprocessing as mp

from .searcher import ScreenshotSearcher, SearchResult
from .rect import get_window_rect


def startup(toggles: mp.Queue, conn: PipeConnection):
    window: gw.Win32Window = gw.getWindowsWithTitle("Idle Slayer")[0]
    if window is None:
        raise Exception("Idle Slayer window not found")
    window.restore()
    window.activate()

    amount = 0
    start = time.time()
    info_toggled = False

    messenger = MessagePasser(conn)
    searcher = ScreenshotSearcher()
    sct = mss.mss()

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
        if not toggles.empty():
            toggles.get()
            info_toggled = not info_toggled

        matches = searcher.search_screenshot(sct_img)

        # add offsets
        for match in matches:
            match["rect"].left += rect.left
            match["rect"].right += rect.left
            match["rect"].top += rect.top
            match["rect"].bottom += rect.top

        messenger.send(matches)

        amount += 1
        if time.time() - start > 1:
            if info_toggled:
                print(f"FPS <= {amount}, current_matches = {matches}")
            amount = 0
            start = time.time()


class MessagePasser:
    def __init__(self, conn: PipeConnection):
        self.conn = conn
        self.sent = set()

    def ack(self):
        while self.conn.poll():
            msg = self.conn.recv()
            self.sent.remove(msg)

    def send(self, msgs: List[SearchResult]):
        self.ack()
        for msg in msgs:
            if msg["sprite"] not in self.sent:
                self.conn.send(msg)
                self.sent.add(msg["sprite"])
