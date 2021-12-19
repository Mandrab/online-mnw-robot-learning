from .Fitness import Fitness
from functools import reduce
from math import sqrt
from operator import sub
from utils import adapt


class CollisionAvoidance(Fitness):
    """Calculate the fitness depending on collision avoidance capabilities"""

    __fitness: float = 0
    __counter: int = 0

    def update(self):
        # get the most near measure and make it in range 0-1
        value = max(sensor.read() for sensor in self.robot.ir_sensors)

        min_value, max_value = self.robot.ir_sensors_range()

        # get motors velocities and make them in range 0-1
        speeds = [motor.speed for motor in self.robot.motors]
        speeds = [adapt(value, (-6.14, 6.14), (0.0, 1.0)) for value in speeds]

        max_proximity = adapt(value, (min_value, max_value), (0, 1))
        average_speed = sum(speeds) / 2.0
        directions = sqrt(abs(reduce(sub, speeds)))

        self.__fitness += (1 - max_proximity) * (1 - directions) * average_speed
        self.__counter += 1

    def value(self) -> float: return 100 * self.__fitness / self.__counter
