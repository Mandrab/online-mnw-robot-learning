from functools import reduce
from math import sqrt
from operator import sub
from optimization.fitness import Fitness as Base
from robot.component import grounds
from robot.component.motor import Motor
from utils import adapt
from world.colors import Colors


PENALTY = 100


class Fitness(Base):
    """
    Calculate the fitness depending on area avoidance capabilities. At each step
    the evaluator calculate fitness according to the following formula:
        p + (1 - d) * s
    where:
        - p in [0, 100]: is the penalty for being in a white area. Normally 0.
        - d in [0, 1]: is the direction of the robot. Straight is 0.
        - s in [-1, 1]: is the speed of the robot. If < 0 the robot is going
          backward, if 0 the robots is still or rotating on itself.
    The fitness are then averaged and the resulting range [-101, 1] is adapted
    to the range [0, 100].
    """

    fitness: float = 0.0
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

        # calculate average speed and direction of the robot
        average_speed = sum(speeds) / 2.0                   # range -1, 1
        directions = sqrt(abs(reduce(sub, speeds)))         # range 0, 1

        # prefer straight and fast movements
        self.fitness += (1 - directions) * average_speed    # range -1, 1
        self.counter += 1

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return adapt(self.fitness / self.counter, (-101, 1), (0, 100))
