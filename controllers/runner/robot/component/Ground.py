from .Sensor import Sensor
from typing import Tuple


class GroundSensor(Sensor):
    """Represents a robot ground sensor"""

    def range(self, **_) -> Tuple[float, float]: return 0, 1000  # todo is it?
