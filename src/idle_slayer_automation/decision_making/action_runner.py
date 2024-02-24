from enum import Enum
import subprocess

class Action(Enum):
    BONUS_STAGE_2 = "bonus_stage_2"

class ActionRunner:
    def __init__(self):
        self._build()
        self.files = {}
        for action in Action:
            self.files[action] = f"actions/{action.value}.actions"

    def _build(self):
        self.exec = "actions/target/release/actions.exe"
        process = subprocess.Popen(
            ["cargo", "build", "--manifest-path", "actions/Cargo.toml", "--release"]
        )
        process.wait()

    def run(self, action: Action):
        assert self.exec is not None
        process = subprocess.Popen(
            [self.exec, "play", "-f", self.files[action]], stdout=subprocess.PIPE
        )
        process.wait()
