from robot.epuck import EPuck
from typing import List


class Manager:
    """Allows to gracefully manage the world."""

    def __init__(self, robot: EPuck, robot_name: str):
        self.robot = robot
        self.robot_name = robot_name
        self.savings = dict()

    def commit(self, ensure: bool = True):
        """Ensure that the modifications took place."""
        self.robot.getFromDef(self.robot_name).resetPhysics()
        if ensure:
            self.robot.step(self.robot.run_frequency.ms)

    def move(self, name: str, to: List[float]):
        """Move the def-specified object to the given position."""
        self.robot.getFromDef(name).getField('translation').setSFVec3f(to)

    def reset(self, name: str):
        """Reset the def-specified object to a previously saved state."""
        assert name in self.savings
        position, rotation = self.savings[name]
        self.move(name, position)
        self.rotate(name, rotation)

    def rotate(self, name: str, to: List[float]):
        """Move the def-specified object to the given rotation."""
        self.robot.getFromDef(name).getField('rotation').setSFRotation(to)

    def save(self, name: str):
        """Save the state (position & rotation) of the def-specified object."""
        self.savings[name] = (
            self.robot.getFromDef(name).getField('translation').getSFVec3f(),
            self.robot.getFromDef(name).getField('rotation').getSFRotation()
        )
