from controller import Robot
from scipy.interpolate import interp1d
from typing import Tuple


class Sensor(str):
    """Represents a robot sensor"""

    # the robot that it is working for/in
    robot: Robot

    # distance sensors lookup table (signal-distance)
    transform = interp1d([65, 306, 676, 1550], [7.0, 3.0, 2.0, 0.0])

    def range(self, proximity: bool = True) -> Tuple[float, float]:
        """
        Return range of read values.
        If raw is true: return [min, max] signal's range (i.e. far, near).
        If raw is false: return [min, max] distance's range (i.e. near, far).
        """
        if proximity:
            return 65, 1550
        return self.transform(1550)[()], self.transform(65)[()]

    def read(self, proximity: bool = True) -> float:
        """
        Returns the sensor reading.

        Parameters:
        -----------
        Proximity: bool
            Define if the function will return a proximity (higher -> nearer) or
            a distance (higher -> farther) value

        Return:
        -------
            A proximity value if 'proximity' is true, a distance value
            otherwise. Both of the values are in the range 0-1550.
        """
        value = self.robot.getDevice(self).getValue()

        # force value in range [65, 1550]
        value = max(min(self.range()), value)
        value = min(max(self.range()), value)

        return value if proximity else self.transform(value)[()]

    def enable(self, update_frequency: int):
        self.robot.getDevice(self).enable(update_frequency)


class Motor(str):
    """Represents a robot motor"""

    # the robot that it is working for/in
    robot: Robot

    @staticmethod
    def range(reverse: bool = False) -> Tuple[float, float]:
        return (6.28, -6.28) if reverse else (-6.28, 6.28)

    @property
    def speed(self) -> float:
        return self.robot.getDevice(self).getVelocity()

    @speed.setter
    def speed(self, value: float):
        self.robot.getDevice(self).setPosition(float('inf'))
        self.robot.getDevice(self).setVelocity(value)
