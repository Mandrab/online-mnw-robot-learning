from robot.transducer.transducer import Transducer
from typing import Tuple


class Motor(str, Transducer[float]):
    """Represents a robot motor"""

    def range(self, reverse: bool = False) -> Tuple[float, float]: return (6.28, -6.28) if reverse else (-6.28, 6.28)

    @property
    def value(self) -> float: return self._robot.getDevice(self).getVelocity()

    @value.setter
    def value(self, value: float):
        self._robot.getDevice(self).setPosition(float('inf'))
        self._robot.getDevice(self).setVelocity(value)
