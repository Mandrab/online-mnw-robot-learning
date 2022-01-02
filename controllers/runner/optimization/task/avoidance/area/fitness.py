from functools import reduce
from math import sqrt
from operator import sub
from optimization.Fitness import Fitness
from robot.component import grounds
from robot.component.Motor import Motor
from utils import adapt
from world.Colors import Colors


PENALTY = 100


class AreaAvoidance(Fitness):
    """Calculate the fitness depending on collision avoidance capabilities"""

    fitness: float = 0
    counter: int = 0

    def update(self):
        # get the highest (nearer) proximity measure and make it in range 0-1
        floor_color = next(iter(grounds(self.robot.sensors))).read()

        # map color to discrete values
        floor_color = Colors.convert(floor_color)

        # if robot goes over illegal areas, penalize it
        if floor_color == Colors.WHITE:
            self.fitness -= PENALTY

        # get motors velocities and make them in range 0-1
        speeds = [motor.speed for motor in self.robot.motors]
        speeds = [adapt(value, Motor.range(), (-1, 1)) for value in speeds]

        # calculate avg speed and direction of the robot
        average_speed = sum(speeds) / 2.0
        directions = sqrt(abs(reduce(sub, speeds)))

        # prefer straight and fast movements
        self.fitness += (1 - directions) * average_speed
        self.counter += 1

    def value(self) -> float:
        return adapt(self.fitness / self.counter, (-101, 1), (0, 100))
