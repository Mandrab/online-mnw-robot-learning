from robot.transducer.transducer import Transducer
from typing import Tuple


class Gripper(str, Transducer[int]):
    """Opens or closes a gripper to possibly catch a catchable object."""

    close: bool = False            # state of the robotic gripper
    state_changed: bool = False    # if the state changed in the last update
    prey = None                    # pointer to the caught prey

    def reset(self):
        self.close = False
        self.state_changed = False
        self.prey = None

    def range(self, reverse: bool = False) -> Tuple[int, int]: return (1, 0) if reverse else (0, 1)

    @property
    def value(self) -> int: return int(self.close)

    @value.setter
    def value(self, value: float):
        self.state_changed = self.close == (value > .5)
        if not self.state_changed:
            return
        self.close = not self.close
