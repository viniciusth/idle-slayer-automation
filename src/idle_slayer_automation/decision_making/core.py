import multiprocessing as mp
from multiprocessing.connection import PipeConnection
from time import sleep
import pyautogui

from idle_slayer_automation.image_processing.searcher import SearchResult, Sprite


def startup(toggles: mp.Queue, conn: PipeConnection):
    do_actions = True

    while True:
        if not toggles.empty():
            toggles.get()
            do_actions = not do_actions

        if not do_actions:
            sleep(0.2)
            continue

        if not conn.poll():
            gameplay()
        else:
            msg: SearchResult = conn.recv()
            handle_event(msg, conn)
            conn.send(msg["sprite"])


def gameplay():
    pyautogui.press("d")
    pyautogui.keyDown("space")
    for _ in range(3):
        pyautogui.press("w")

    pyautogui.keyUp("space")

    for _ in range(3):
        pyautogui.press("w")

def handle_event(msg: SearchResult, _conn: PipeConnection):
    match msg["sprite"]:
        case Sprite.CHEST | Sprite.SAVER:
            # TODO: implement chest minigame solver
            pass
        case Sprite.SILVER_BOX:
            pyautogui.keyDown("space")
            sleep(1)
            pyautogui.keyUp("space")
        case Sprite.SILVER_BOXES | Sprite.OFFLINE_EXTRA:
            middle_x = msg["rect"].left + msg["rect"].width / 2
            middle_y = msg["rect"].top + msg["rect"].height / 2
            pyautogui.click(middle_x, middle_y, duration=0.05)
            sleep(0.2)
        case x:
            raise Exception(f"Unknown sprite {x}")
