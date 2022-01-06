from functools import reduce
from math import sqrt
from operator import add
from optimization.fitness import Fitness as Base
from robot.body import EPuck


class Fitness(Base):
    """Calculate the distance travelled by the robot"""

    # travelled distance
    distance: float = 0.0

    def __init__(self, robot: EPuck):
        """Initialize the evaluator and save the robot instance"""
        Base.__init__(self, robot)

        # get robot node and get its position field
        self.translation = robot.getFromDef('evolvable').getField('translation')

        # get position of the robot at the step (x, y, z)
        self.position = self.translation.getSFVec3f()[:2]

    def update(self):
        # get position of the robot at the step (x, y, z)
        new_position = self.translation.getSFVec3f()[:2]

        # update distance adding travelled distance (euclidean)
        points = zip(self.position, new_position)
        self.distance += sqrt(reduce(add, [pow(x - y, 2) for x, y in points]))

        # update position
        self.position = new_position

    def value(self) -> float: return self.distance
