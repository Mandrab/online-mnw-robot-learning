from functools import reduce
from math import sqrt
from operator import sub
from optimization.Fitness import Fitness
from robot.component.Motor import Motor
from utils import adapt


class CollisionAvoidance(Fitness):
    """Calculate the fitness depending on collision avoidance capabilities"""

    __fitness: float = 0
    __counter: int = 0

    def update(self):
        # get the highest (nearer) proximity measure and make it in range 0-1
        max_proximity = max(s.read(normalize=True) for s in self.robot.sensors)

        # get motors velocities and make them in range 0-1
        speeds = [motor.speed for motor in self.robot.motors]
        speeds = [adapt(value, Motor.range()) for value in speeds]

        average_speed = sum(speeds) / 2.0
        directions = sqrt(abs(reduce(sub, speeds)))

        self.__fitness += (1 - max_proximity) * (1 - directions) * average_speed
        self.__counter += 1

    def value(self) -> float: return 100 * self.__fitness / self.__counter
