from abc import abstractmethod
from controller import Robot
from typing import Tuple
from utils import adapt


class Sensor(str):
    """
    Represents a sensor of the robot and act as a proxy with more user friendly
    methods.
    """

    # the robot that it is part of
    robot: Robot

    @abstractmethod
    def range(self) -> Tuple[float, float]:
        """Returns the sensor working output range."""
        return NotImplemented()

    def read(self, normalize: bool = False) -> float:
        """Returns the sensor reading."""

        value = self.robot.getDevice(self).getValue()
        return adapt(value, self.range()) if normalize else value

    def enable(self, update_frequency: int = 1):
        """Enable the sensors to perceive information at the given frequency."""

        self.robot.getDevice(self).enable(update_frequency)

    def exists(self) -> bool:
        """Check if the given device is available on the given robot."""

        return self.robot.getDevice(self) is not None
