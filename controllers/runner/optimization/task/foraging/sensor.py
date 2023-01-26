from robot.transducer.transducer import Transducer
from typing import Tuple
from optimization.task.foraging.util import is_facing


class PreySensor(str, Transducer[bool]):
    """Perceive a catchable object in front of the robot."""

    def range(self, reverse: bool = False) -> Tuple[bool, bool]: return (True, False) if reverse else (False, True)

    @property
    def value(self) -> bool:
        # find the catchable objects (hardcoded)
        objects = [self._robot.getFromDef(f'c{i}') for i in range(24)]

        # return the true if any object is faced by the robot, false otherwise
        return next(filter(bool, map(lambda _: is_facing(self._robot, _), objects)), False)

    @property
    def normalized_value(self): return 1 if self.value else 0
