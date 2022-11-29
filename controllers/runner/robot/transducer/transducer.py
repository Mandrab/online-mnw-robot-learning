from abc import ABC, abstractmethod
from controller import Robot
from typing import Generic, Tuple, TypeVar
from utils import adapt

T = TypeVar("T")


class Transducer(ABC, Generic[T]):
    """
    Represents a component of the robot that can be set or read.
    In case of readable (often a sensor), the value may belong
    to a given range.
    """

    # represents the parent robot of the transducer
    _robot: Robot

    def initialize(self, robot: Robot):
        """Initialize the transducer setting the parent robot."""

        self._robot = robot

    @abstractmethod
    def range(self, reverse: bool = False) -> Tuple[T, T]:
        """Returns the transducer working range."""
        return NotImplemented()

    @property
    @abstractmethod
    def value(self) -> T:
        """Returns the transducer state."""
        return NotImplemented()

    @property
    def normalized_value(self):
        """Return the transducer state in range [0-1]."""
        return adapt(self.value, self.range())

    @value.setter
    @abstractmethod
    def value(self, v: T):
        """Set the transducer state."""
        NotImplemented()
