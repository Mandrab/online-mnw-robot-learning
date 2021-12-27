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
        if not self.__field(name, 'translation'):
            return None
        self.robot.getFromDef(name).getField('translation').setSFVec3f(to)

    def position(self, name: str):
        """Get the def-specified object's position."""
        if not self.__field(name, 'translation'):
            return None
        return self.robot.getFromDef(name).getField('translation').getSFVec3f()

    def reset(self, name: str):
        """Reset the def-specified object to a previously saved state."""
        assert name in self.savings
        position, rotation = self.savings[name]
        self.move(name, position)
        self.rotate(name, rotation)

    def rotate(self, name: str, to: List[float]):
        """Move the def-specified object to the given rotation."""
        if not self.__field(name, 'rotation'):
            return None
        self.robot.getFromDef(name).getField('rotation').setSFRotation(to)

    def save(self, name: str):
        """Save the state (position & rotation) of the def-specified object."""
        if (
            not self.__field(name, 'translation')
            or
            not self.__field(name, 'rotation')
        ):
            return None
        self.savings[name] = (
            self.robot.getFromDef(name).getField('translation').getSFVec3f(),
            self.robot.getFromDef(name).getField('rotation').getSFRotation()
        )

    def __node(self, name: str): return self.robot.getFromDef(name)

    def __field(self, node: str, field: str):
        return self.__node(node) and self.__node(node).getField(field)
