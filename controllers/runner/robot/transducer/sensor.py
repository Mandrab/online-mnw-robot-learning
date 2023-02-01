from abc import abstractmethod
from controller import Robot
from robot.transducer.transducer import Transducer
from typing import Tuple


class Sensor(str, Transducer[float]):
    """Represents a sensor of the robot and act as a proxy with more user-friendly methods."""

    def initialize(self, robot: Robot, update_frequency: int = 1):
        """Enable the sensors to perceive information at the given frequency."""

        Transducer.initialize(self, robot)
        self._robot.getDevice(self).enable(update_frequency)

    @abstractmethod
    def range(self, reverse: bool = False) -> Tuple[float, float]: return NotImplemented()

    @property
    def value(self) -> float: return self._robot.getDevice(self).getValue()

    @value.setter
    def value(self, v: float): pass

    def exists(self) -> bool:
        """Check if the given device is available on the given robot."""

        return self._robot.getDevice(self) is not None


class IRSensor(Sensor):
    """Represents a robot IR (proximity) sensor"""

    def range(self, reverse: bool = False) -> Tuple[float, float]: return (0, 4095) if not reverse else (4095, 0)


class USSensor(Sensor):
    """Represents a robot Ultrasonic sensor"""

    def range(self, reverse: bool = False) -> Tuple[float, float]: return (0, 1000) if not reverse else (1000, 0)


class GroundSensor(IRSensor):
    """Represents a robot ground sensor"""

    def range(self, reverse: bool = False) -> Tuple[float, float]: return (0, 1000) if not reverse else (1000, 0)
