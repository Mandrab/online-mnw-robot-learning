from .sensor import Sensor
from typing import Tuple


class GroundSensor(Sensor):
    """Represents a robot ground sensor"""

    # todo: in area avoidance it has to be influential: 0-1e3; in t-maze it has
    # to be less influential: 0, 1e4
    def range(self, **_) -> Tuple[float, float]: return 0, 1e4
