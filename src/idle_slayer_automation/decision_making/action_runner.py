from collections import namedtuple
from enum import Enum
from typing import List


class Action(Enum):
    BONUS_STAGE_2 = "bonus_stage_2"


ProcedureStep = namedtuple("ProcedureStep", ["begin", "end", "action"])


class Procedure:
    def __init__(self, filename: str):
        self.events: List[ProcedureStep] = []
        last_event_idx = {}
        with open(filename, "r") as f:
            first_timestamp = None
            for line in f.readlines():
                timestamp, ty, key = line.split(":")

                if first_timestamp is None:
                    first_timestamp = int(timestamp)
                # convert to time since first event
                timestamp = int(timestamp) - first_timestamp

                if ty == "+":
                    last_event_idx[key] = len(self.events)
                    self.events.append(ProcedureStep(timestamp, None, key))
                elif ty == "-":
                    idx = last_event_idx.pop(key)
                    self.events[idx] = self.events[idx]._replace(end=timestamp)
        assert (
            len(last_event_idx) == 0
        ), f"Unmatched events: {[self.events[i] for i in last_event_idx.values()]}"

    def __iter__(self):
        return iter(self.events)


class ActionRunner:
    def __init__(self):
        self.procedures = {}
        for action in Action:
            self.procedures[action] = Procedure(f"actions/{action.value}.actions")
