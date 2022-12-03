from functools import reduce
from logger import logger
from math import sqrt
from operator import sub
from optimization.fitness import Fitness as Base
from utils import adapt

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


def _f_fitness(actuator, robot) -> float:

    # calculate if the robot is on the nest through its position
    # it resolves some problems of the ground sensor of webots
    x, _, z = robot.getFromDef('evolvable').getPosition()
    distance = sqrt(x ** 2 + z ** 2)
    on_nest = -.475 < distance < .475

    if actuator.captured:

        if on_nest:
            logger.info("wrong capture (no penalty)")
        else:
            logger.info("correct capture")

    if actuator.deposited:

        if on_nest:
            logger.info("correct deposit")

            robot.simulationSetMode(robot.SIMULATION_MODE_PAUSE)
        else:
            logger.info("wrong deposit")

    # check if the robot just picked up an object in the white region
    result = actuator.captured * (not on_nest) * PRIZE

    # check if the robot deposited an object in the correct region
    result += actuator.deposited * (PRIZE if on_nest else PENALTY)

    return result


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities together with the foraging behavior."""

    fitness: float = 0.0
    counter: int = 0

    def update(self):

        # separate different type of sensors
        irs = filter(lambda sensor: sensor.startswith('ps'), self.robot.sensors)

        # separate gripper and motor actuators
        a = next(filter(lambda actuator: actuator.startswith('gripper'), self.robot.motors))
        ms = filter(lambda actuator: actuator.endswith('motor'), self.robot.motors)

        # calculate the collision avoidance fitness
        self.fitness += _ca_fitness(irs, ms)

        # calculate the foraging fitness
        self.fitness += _f_fitness(a, self.robot)

        self.counter += 1

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return 100 * self.fitness / self.counter
