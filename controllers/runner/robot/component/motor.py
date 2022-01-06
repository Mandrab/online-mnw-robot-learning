from controller import Robot
from typing import Tuple


class Motor(str):
    """Represents a robot motor"""

    # the robot that it is working for/in
    robot: Robot

    @staticmethod
    def range(reverse: bool = False) -> Tuple[float, float]:
        """Return motor working input range."""
        return (6.28, -6.28) if reverse else (-6.28, 6.28)

    @property
    def speed(self) -> float:
        """Return motor actual running speed."""
        return self.robot.getDevice(self).getVelocity()

    @speed.setter
    def speed(self, value: float):
        """Set motor running speed."""
        self.robot.getDevice(self).setPosition(float('inf'))
        self.robot.getDevice(self).setVelocity(value)
