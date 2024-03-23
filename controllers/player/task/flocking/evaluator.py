from _operator import sub
from functools import reduce
from inout import configs
from math import sqrt
from webots.robot import get_actuators, get_sensors, robot


MAX_OUTPUT = configs["actuators"]["max_output"]


def evaluate():
    # get the proximity measures in range 0-1
    proximity = [s.getValue() / 1000 for s in get_sensors(robot).values()]

    # get motors velocities and make them in range 0-1
    speeds = [a.getVelocity() / MAX_OUTPUT for a in get_actuators(robot).values()]
    average_speed = sum(speeds) / 2.0
    directions = 1 - abs(reduce(sub, speeds))

    # the desired distance is 0.5: if more or less give penalty
    proximity = [1 - p if p > .5 else p for p in proximity]

    return sqrt(sum(proximity) / len(proximity)) * directions * average_speed


__all__ = "evaluate",
