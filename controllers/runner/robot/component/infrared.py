from .sensor import Sensor
from scipy.interpolate import interp1d
from typing import Tuple
from utils import adapt


class IRSensor(Sensor):
    """Represents a robot IR (proximity) sensor"""

    # proximity/signal-distance converter (spline)
    spline = interp1d([65, 306, 676, 1550], [7.0, 3.0, 2.0, 0.0])

    def range(self, **others) -> Tuple[float, float]:
        """
        Return range of read values.
        By default it returns proximity range: [65, 1550] (farther is lower).
        If distance is specified, return in range [0, 7] (farther is higher).
        """
        if not others.get('distance', False):
            return 65, 1550
        return self.spline(1550)[()], self.spline(65)[()]

    def read(self, normalize: bool = False, **others) -> float:
        """
        Returns the sensor reading.

        Parameters:
        -----------
        distance: bool
            Define if the function will return a proximity (higher -> nearer) or
            a distance (higher -> farther) value.

        Return:
        -------
            A distance value if 'distance' is true, a proximity value otherwise.
        """

        # force value in range [65, 1550]
        read = min(max(self.range()), max(min(self.range()), Sensor.read(self)))

        # get desired value: proximity or distance
        read = self.spline(read)[()] if others.get('distance', False) else read

        # if required, normalize the result
        return adapt(read, self.range(**others), (0, 1)) if normalize else read
