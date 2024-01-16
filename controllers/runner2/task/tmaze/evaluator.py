from inout.logger import logger
from task.tmaze.colors import Colors
from webots.robot import get_sensors, robot


def evaluate():

    # get first ground-sensor reading
    floor_level = get_sensors(robot)["gs0"].getValue()

    # map reading to discrete values
    floor_level = Colors.convert(floor_level)

    # if the webots is in neutral zone, it cannot gain scores
    if floor_level == Colors.GRAY:
        return 0

    # if the target (black->white; white->black) has been reached (we
    # consider 3 color) increase fitness, otherwise decrease it
    if floor_level != evaluate.__dict__["initial_color"]:

        if not evaluate.__dict__["reach_flag"]:
            evaluate.__dict__["reach_flag"] = True
            logger.info('On correct end-point')

        return 2
    return -1


__all__ = "evaluate",