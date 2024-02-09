import typer
import multiprocessing as mp
from pynput import keyboard

from idle_slayer_automation.decision_making.core import (
    startup as decision_making_startup,
)
from idle_slayer_automation.image_processing.core import (
    startup as image_processing_startup,
)


def main():
    eye_msgs = mp.Queue()
    info_msgs = mp.Queue()
    brain = mp.Process(target=decision_making_startup, args=(eye_msgs,))
    eyes = mp.Process(target=image_processing_startup, args=(info_msgs, eye_msgs))
    brain.start()
    eyes.start()

    def on_press(key):
        if key == keyboard.Key.esc:
            brain.terminate()
            eyes.terminate()
            return False
        elif keyboard.KeyCode.from_char("i"):
            info_msgs.put("toggle")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    typer.run(main)
