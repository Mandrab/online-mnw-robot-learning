from functools import reduce
from logger import logger
from math import sqrt
from operator import sub
from optimization.fitness import Fitness as Base
from robot.transducer import grounds
from utils import adapt
from world.colors import Colors

PENALTY = -100
PRIZE = 50


def _ca_fitness(sensors, motors) -> float:

    # get the highest (nearer) proximity measure and make it in range 0-1
    max_proximity = max(s.normalized_value for s in sensors)

    # get motors velocities and make them in range 0-1
    speeds = [adapt(motor.value, in_range=motor.range()) for motor in motors]

    average_speed = sum(speeds) / 2.0
    directions = 1 - abs(reduce(sub, speeds))

    return (1 - sqrt(max_proximity)) * directions * average_speed


def _f_fitness(sensors, actuator) -> float:

    # get first ground-sensor reading and map to discrete values
    floor_level = Colors.convert(next(iter(grounds(sensors))).value)

    # check if the robot just picked up an object in the black region
    if actuator.captured and floor_level == Colors.WHITE:
        logger.info("capture")
        return PRIZE

    # check if the robot deposited an object in the white region
    if actuator.deposited and floor_level == Colors.BLACK:
        logger.info("correct deposit")
        return PRIZE

    # give a penalty if the robot deposited the object in a region different from the white one
    if actuator.deposited and floor_level == Colors.WHITE:
        logger.info("wrong deposit")
        return PENALTY

    return 0


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities together with the foraging behavior."""

    fitness: float = 0.0
    counter: int = 0

    def update(self):

        # separate different type of sensors
        irs = filter(lambda sensor: sensor.startswith('ps'), self.robot.sensors)
        gs = filter(lambda sensor: sensor.startswith('gs'), self.robot.sensors)

        # separate gripper and motor actuators
        a = next(filter(lambda actuator: actuator.startswith('gripper'), self.robot.motors))
        ms = filter(lambda actuator: actuator.endswith('motor'), self.robot.motors)

        # calculate the collision avoidance fitness
        self.fitness += _ca_fitness(irs, ms)

        # calculate the foraging fitness
        self.fitness += _f_fitness(gs, a)

        self.counter += 1

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return 100 * self.fitness / self.counter
