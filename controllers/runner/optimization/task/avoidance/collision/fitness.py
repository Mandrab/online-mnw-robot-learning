from functools import reduce
from math import sqrt
from operator import sub
from optimization.Fitness import Fitness as Base
from robot.component.Motor import Motor
from utils import adapt


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities"""

    fitness: float = 0
    counter: int = 0

    def update(self):
        # get the highest (nearer) proximity measure and make it in range 0-1
        max_proximity = max(s.read(normalize=True) for s in self.robot.sensors)

        # get motors velocities and make them in range 0-1
        speeds = [motor.speed for motor in self.robot.motors]
        speeds = [adapt(value, Motor.range()) for value in speeds]

        average_speed = sum(speeds) / 2.0
        directions = sqrt(abs(reduce(sub, speeds)))

        self.fitness += (1 - max_proximity) * (1 - directions) * average_speed
        self.counter += 1

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return 100 * self.fitness / self.counter
