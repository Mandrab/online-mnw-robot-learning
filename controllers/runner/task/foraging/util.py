from math import sqrt
from webots.robot import get_sensors


def on_nest(robot):
    pgs, ngs = get_sensors(robot)["gs0"], get_sensors(robot)["gs2"]
    return pgs.getValue() < 800 and ngs.getValue() > 200


def on_plate(robot):
    pgs, ngs = get_sensors(robot)["gs0"], get_sensors(robot)["gs2"]
    return pgs.getValue() > 900 and ngs.getValue() < 100


def is_above(robot, obj) -> bool:
    rx, _, ry = robot.getFromDef("evolvable").getPosition()
    ox, _, oy = obj.getPosition()

    distance = sqrt((rx - ox) ** 2 + (ry - oy) ** 2)

    return distance <= 0.075 + 0.037
