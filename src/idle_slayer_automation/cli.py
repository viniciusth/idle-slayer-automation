import typer
import multiprocessing as mp
import time
from pynput import keyboard

from idle_slayer_automation.decision_making.core import (
    startup as decision_making_startup,
)
from idle_slayer_automation.image_processing.core import (
    startup as image_processing_startup,
)

app = typer.Typer()


@app.command()
def run():
    (brain_conn, eyes_conn) = mp.Pipe()
    (brain_toggles, eye_toggles) = (mp.Queue(), mp.Queue())
    brain = mp.Process(
        target=decision_making_startup,
        args=(
            brain_toggles,
            brain_conn,
        ),
    )
    eyes = mp.Process(target=image_processing_startup, args=(eye_toggles, eyes_conn))
    brain.start()
    eyes.start()

    def on_press(key):
        if key == keyboard.Key.esc or key == keyboard.KeyCode.from_char("q"):
            try:
                brain.terminate()
                eyes.terminate()
            except Exception:
                pass
            return False
        elif key == keyboard.KeyCode.from_char("i"):
            eye_toggles.put("info")
        elif key == keyboard.KeyCode.from_char("a"):
            brain_toggles.put("actions")
        elif key == keyboard.KeyCode.from_char("j"):
            brain_toggles.put("jump_strategy")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


@app.command()
def record_keys(file: str = "keys.txt"):
    with open(file, "w") as f:
        start_time = None

        currently_pressed = set()

        def on_press(key):
            if key == keyboard.Key.esc:
                return False
            if start_time == None and key == keyboard.KeyCode.from_char("s"):
                return

            key = str(key) if key != keyboard.Key.space else "'space'"
            if key in currently_pressed:
                return
            currently_pressed.add(key)
            f.write(f"{time.time_ns() - start_time}:+:{key}\n")

        def on_release(key):
            nonlocal start_time
            if start_time == None and key == keyboard.KeyCode.from_char("s"):
                start_time = time.time_ns()
                print("started recording")
                return
            key = str(key) if key != keyboard.Key.space else "'space'"
            currently_pressed.remove(key)
            f.write(f"{time.time_ns() - start_time}:-:{key}\n")

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            print("press 's' to start recording, 'esc' to stop")
            listener.join()


@app.callback()
def main():
    pass


if __name__ == "__main__":
    app()
