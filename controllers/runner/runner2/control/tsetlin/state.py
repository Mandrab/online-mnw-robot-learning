from __future__ import annotations
from enum import Enum
from typing import Dict


class State:

    class Type(Enum):
        OPERATION = 0
        ADAPTATION = 1
        EXPLORATION = 2

    class Transition(Enum):
        PERFORMANCE_INCREASE = 0
        PERFORMANCE_STAGNATION = 1
        PERFORMANCE_DECREASE = 2

    type: Type
    transition: Dict[Transition, int]

    def __init__(self, state_type: Type = Type.OPERATION):
        self.type = state_type
        self.transition = {}


def str2phase(s: str) -> State.Type:
    if s == "exploration":
        return State.Type.EXPLORATION
    elif s == "adaptation":
        return State.Type.ADAPTATION
    return State.Type.OPERATION


__all__ = "State", "str2phase"
