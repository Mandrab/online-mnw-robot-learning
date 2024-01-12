from functools import reduce
from inout.loader import configs
from math import sqrt
from operator import sub
from replica import range2range
from robot import get_actuators, get_sensors, robot

MAX_INPUT = configs["max_input"]
MAX_OUTPUT = configs["max_output"]


def evaluate():
    # get the highest (nearer) proximity measure and make it in range 0-1
    max_proximity = max(s.getValue() for s in get_sensors(robot).values())
    max_proximity = range2range(max_proximity, (0, MAX_INPUT))

    # get motors velocities and make them in range 0-1
    speeds = [range2range(a.getVelocity(), (0, MAX_OUTPUT)) for a in get_actuators(robot).values()]

    average_speed = sum(speeds) / 2.0
    directions = 1 - abs(reduce(sub, speeds))

    return (1 - sqrt(max_proximity)) * directions * average_speed
