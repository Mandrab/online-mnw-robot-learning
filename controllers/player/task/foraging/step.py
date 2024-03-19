from inout.loader import configs
from simulation.replica import Replica, run
from task.foraging.evaluator import evaluate
from task.foraging.util import is_above, on_nest
from webots.robot import get_actuators
from webots.supervisor import supervisor

TASK_TYPE = configs["task"]["type"]

if TASK_TYPE == "FORAGING":
    # save the starting position of the objects to be able to restore them once deposited
    objects = tuple(supervisor.getFromDef(f"P{i}") for i in range(24))
    starting_positions = tuple(list(map(float, o.getField("description").getSFString().split())) for o in objects)


def step(replica: Replica, _: int) -> Replica:

    # run this replica in a simulation step
    run(replica)

    # check a capture and update the world
    check_capture(supervisor, objects)

    # evaluate the replica performance in this simulation step
    replica.configuration.performance += evaluate()

    # check a release and update the world
    check_release(supervisor, objects)

    # returns the replica with the updated performance evaluation
    return replica


def check_capture(robot, preys):

    # find the gripper between the actuators
    gripper = get_actuators(robot)["gripper"]

    # if the robot already hold a prey it cannot hold another one
    if gripper.get_prey_index() is not None:
        return

    # if the robot didn't close its gripper, it couldn't capture anything
    if not gripper.is_state_changed() or not gripper.is_close():
        return

    # find the preys (hardcoded quantity) and get the possibly first element that the robot hover
    prey_index = next((i for i in range(24) if is_above(robot, preys[i])), None)

    # if the robot does not hover any prey, it cannot capture anything
    if prey_index is None:
        return

    # temporary remove the object from the environment (captured)
    preys[prey_index].getField("translation").setSFVec3f([0, 1e5, 0])

    # memorize the capture
    gripper.set_prey_index(prey_index)


def check_release(robot, preys):

    # find the gripper between the actuators
    gripper = get_actuators(robot)["gripper"]

    # the robot does not hold any prey, it cannot release anything
    if gripper.get_prey_index() is None:
        return

    # if the robot didn't open its gripper, it cannot release anything
    if not gripper.is_state_changed() or gripper.is_close():
        return

    # if webots is on the nest, reset the object position to its origin
    # otherwise, free the prey in the webots position
    rx, _, ry = robot.getFromDef("evolvable").getPosition()

    position = starting_positions[gripper.get_prey_index()] if on_nest(robot) else [rx, 0.001, ry]
    preys[gripper.get_prey_index()].getField("translation").setSFVec3f(position)

    gripper.set_prey_index(None)


__all__ = "step",
