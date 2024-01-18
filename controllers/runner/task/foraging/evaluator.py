from inout.loader import configs
from inout.logger import logger
from task.foraging.util import on_nest
from webots.robot import get_actuators, robot

MAX_PRIZE = configs["task"]["max_step_prize"]
MAX_PENALTY = configs["task"]["max_step_penalty"]


def evaluate():

    gripper = get_actuators(robot)["gripper"]

    # no interaction with a prey or the environment correspond to 0 fitness
    if not gripper.is_state_changed():
        return 0

    # if the gripper closes with a prey under it, prize it
    if gripper.is_close() and gripper.get_prey_index() is not None:
        logger.info("capture")
        return MAX_PRIZE

    # if the gripper opens while holding a prey, check if it is opening on the nest:
    # if yes, prize it; otherwise give it a penalty (this avoids sequences
    # of captures and leaves outside the nest to increase the performance)
    if not gripper.is_close() and gripper.get_prey_index() is not None:
        logger.info(f"{'correct' if on_nest(robot) else 'wrong'} deposit")
        return (2 * MAX_PRIZE) if on_nest(robot) else MAX_PENALTY

    return 0
