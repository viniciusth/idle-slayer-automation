import multiprocessing as mp
from multiprocessing.connection import PipeConnection
from time import sleep
import pyautogui
from idle_slayer_automation.decision_making.action_runner import Action, ActionRunner
from idle_slayer_automation.image_processing.rect import WindowRect

from idle_slayer_automation.image_processing.searcher import SearchResult, Sprite

RUNNER = ActionRunner()


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


def click_middle(rect: WindowRect):
    middle_x, middle_y = rect.left + rect.width / 2, rect.top + rect.height / 2
    pyautogui.click(middle_x, middle_y, duration=0.05)


def handle_event(conn: PipeConnection):
    msg: SearchResult = conn.recv()
    match msg["sprite"]:
        case Sprite.CHEST | Sprite.SAVER:
            conn.send(msg["sprite"])
            chest_hunt(conn)
            return
        case Sprite.SILVER_BOX | Sprite.BOX:
            sleep(0.5)
            pyautogui.keyDown("space")
            sleep(1)
            pyautogui.keyUp("space")
        case Sprite.SILVER_BOXES | Sprite.OFFLINE_EXTRA | Sprite.CLOSE_CHEST_HUNT:
            click_middle(msg["rect"])
            sleep(0.2)
        case Sprite.BONUS_STAGE | Sprite.START_BONUS | Sprite.START_BONUS_2:
            conn.send(msg["sprite"])
            bonus_stage(conn)
            return
        case Sprite.SECOND_WIND:
            click_middle(msg["rect"])
            RUNNER.run(Action.BONUS_STAGE_2)
            conn.send(msg["sprite"])
            return
        case x:
            raise Exception(f"Unexpected sprite {x}")

    conn.send(msg["sprite"])


def get(conn: PipeConnection):
    if conn.poll(15):
        return conn.recv()
    return None


def chest_hunt(conn: PipeConnection):
    # sleep for a while for the minigame to actually start
    sleep(10)
    # currently I have only 1 extra click before saver
    non_saver_clicks = 1
    msg = conn.recv()
    for _ in range(non_saver_clicks):
        while not msg["sprite"] == Sprite.CHEST:
            conn.send(msg["sprite"])
            msg = get(conn)
            if msg is None:
                return

        click_middle(msg["rect"])
        sleep(2.5)

    tries = 20
    while (not msg["sprite"] == Sprite.SAVER or msg["certainty"] < 0.95) and tries > 0:
        conn.send(msg["sprite"])
        msg = get(conn)
        if msg is None:
            return
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
        if msg["sprite"] == Sprite.CLOSE_CHEST_HUNT:
            return
        sleep(1)


def bonus_stage(conn: PipeConnection):
    jumps = 3
    while jumps > 0:
        if jumps == 3:
            sleep(0.5)
        pyautogui.keyDown("space")
        sleep(1)
        pyautogui.keyUp("space")
        jumps -= 1

    msg = get(conn)
    if msg is None:
        return
    while (
        not msg["sprite"] == Sprite.START_BONUS
        and not msg["sprite"] == Sprite.START_BONUS_2
    ):
        conn.send(msg["sprite"])
        msg = get(conn)
        if msg is None:
            return

    # Right to left drag
    rect: WindowRect = msg["rect"]
    if msg["sprite"] == Sprite.START_BONUS:
        pyautogui.click(rect.right - 10, rect.top + rect.height / 2, duration=0.1)
        pyautogui.dragTo(rect.left, rect.top + rect.height / 2, duration=0.5)
    else:
        pyautogui.click(rect.left + 10, rect.top + rect.height / 2, duration=0.1)
        pyautogui.dragTo(rect.right, rect.top + rect.height / 2, duration=0.5)

    # wait for the bonus stage to start
    sleep(1)

    RUNNER.run(Action.BONUS_STAGE_2)
    sleep(5)

    conn.send(msg["sprite"])
