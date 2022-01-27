from .sensor import Sensor
from typing import Tuple


class IRSensor(Sensor):
    """Represents a robot IR (proximity) sensor"""

    def range(self) -> Tuple[float, float]: return 0, 4095
