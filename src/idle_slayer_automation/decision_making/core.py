import multiprocessing as mp
from multiprocessing.connection import PipeConnection
from time import sleep
import pyautogui
from idle_slayer_automation.image_processing.rect import WindowRect

from idle_slayer_automation.image_processing.searcher import SearchResult, Sprite


def startup(toggles: mp.Queue, conn: PipeConnection):
    do_actions = True
    jump_strategy = 0

    while True:
        while not toggles.empty():
            msg = toggles.get()
            if msg == "actions":
                do_actions = not do_actions
            elif msg == "jump_strategy":
                jump_strategy = (jump_strategy + 1) % 3

        if not do_actions:
            sleep(0.2)
            continue

        while conn.poll():
            handle_event(conn)

        gameplay(jump_strategy)


def gameplay(jump_strategy: int):
    match jump_strategy:
        # Long jumps, better for getting all coins and killing non-big enemies
        case 0:
            pyautogui.press("d")
            pyautogui.keyDown("space")
            for _ in range(3):
                pyautogui.press("w")

            pyautogui.keyUp("space")

            for _ in range(3):
                pyautogui.press("w")

        # Short jumps, still gets most coins and enemies, good for hills giants
        case 1:
            pyautogui.press("d")
            for _ in range(5):
                pyautogui.press("w")

        # Short jumps with a delay, good for killing smaller big enemies (fairy)
        case 2:
            pyautogui.press("d")
            for _ in range(5):
                pyautogui.press("w")
                sleep(0.03)
            sleep(0.3)


def handle_event(conn: PipeConnection):

    def click_middle(rect: WindowRect):
        middle_x, middle_y = rect.left + rect.width / 2, rect.top + rect.height / 2
        pyautogui.click(middle_x, middle_y, duration=0.05)

    msg: SearchResult = conn.recv()
    match msg["sprite"]:
        case Sprite.CHEST | Sprite.SAVER:
            # sleep for a while for the minigame to actually start
            sleep(10)
            # currently I have only 1 extra click before saver
            non_saver_clicks = 1
            for _ in range(non_saver_clicks):
                while not msg["sprite"] == Sprite.CHEST:
                    conn.send(msg["sprite"])
                    msg = conn.recv()

                click_middle(msg["rect"])
                sleep(1.5)

            tries = 20
            while (
                not msg["sprite"] == Sprite.SAVER or msg["certainty"] < 0.95
            ) and tries > 0:
                conn.send(msg["sprite"])
                msg = conn.recv()
                tries -= 1

            click_middle(msg["rect"])
            conn.send(msg["sprite"])
            sleep(2)

            # after this we should have the saver and start playing the minigame normally.
            while conn.poll():
                msg = conn.recv()
                if (
                    msg["sprite"] == Sprite.CHEST
                    or msg["sprite"] == Sprite.CLOSE_CHEST_HUNT
                    or msg["sprite"] == Sprite.SAVER
                ):
                    click_middle(msg["rect"])
                conn.send(msg["sprite"])
                sleep(1)
            return
        case Sprite.SILVER_BOX | Sprite.BOX:
            sleep(0.5)
            pyautogui.keyDown("space")
            sleep(1)
            pyautogui.keyUp("space")
        case Sprite.SILVER_BOXES | Sprite.OFFLINE_EXTRA | Sprite.CLOSE_CHEST_HUNT:
            click_middle(msg["rect"])
            sleep(0.2)
        case Sprite.BONUS_STAGE:
            # skip bonus stages
            sleep(10)
        case x:
            raise Exception(f"Unknown sprite {x}")

    conn.send(msg["sprite"])
