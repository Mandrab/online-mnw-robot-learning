from abc import abstractmethod
from robot.epuck import EPuck


class Fitness:
    """
    Define the structure of a fitness calculator.
    The measure is evaluated during an epoch duration.
    """

    def __init__(self, robot: EPuck):
        self.robot = robot

    @abstractmethod
    def update(self):
        """
        Update the fitness measure by looking at the actual robot state.
        To be called after each simulation step.
        """
        pass

    @abstractmethod
    def value(self) -> float:
        """Get fitness measured so far."""
        pass
