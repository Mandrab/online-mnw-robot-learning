from functools import reduce
from math import sqrt
from operator import sub
from optimization.fitness import Fitness as Base
from utils import adapt


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities"""

    fitness: float = 0
    counter: int = 0

    def update(self):
        # get the highest (nearer) proximity measure and make it in range 0-1
        max_proximity = max(s.normalized_value for s in self.robot.sensors)

        # get motors velocities and make them in range 0-1
        speeds = [adapt(motor.value, in_range=motor.range()) for motor in self.robot.motors]

        average_speed = sum(speeds) / 2.0
        directions = 1 - abs(reduce(sub, speeds))

        self.fitness += (1 - sqrt(max_proximity)) * directions * average_speed
        self.counter += 1

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return 100 * self.fitness / self.counter
