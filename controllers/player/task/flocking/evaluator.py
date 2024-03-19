from webots.robot import get_sensors, robot


def evaluate():
    # get the proximity measures in range 0-1
    proximity = [s.getValue() / 1000 for s in get_sensors(robot).values()]

    # the desired distance is 0.5: if more or less give penalty
    proximity = [1 - p if p > .5 else p for p in proximity]

    # calculate the average proximity
    return sum(proximity) / len(proximity)


__all__ = "evaluate",
