from logger import logger
from math import sqrt
from optimization.individual import Individual
from optimization.task.foraging.util import on_nest, on_plate
from optimization.task.foraging.gripper import Gripper
from robot.robot import run


def live(instance: Individual, duration: int):
    """
    Evaluate the individual in the foraging task.
    Runs the robot and collect the resulting score of the step.
    """

    # save the starting position of the objects to be able to restore them once deposited
    starting_positions = [instance.body.getFromDef(f'P{i}').getField('translation').getSFVec3f() for i in range(24)]

    # iterate for the epoch duration
    for counter in range(duration):

        # run the individual
        stimulus, response = run(instance)

        # evaluate the actions
        instance.biography.evaluator.update()

        # correct world state
        update_world(instance.body, starting_positions)

        # save the biography for the step
        instance.biography.stimulus.append(stimulus)
        instance.biography.response.append(response)

        logger.cortex_plot(instance)

    logger.info('fitness: ' + str(instance.biography.evaluator.value()))


def update_world(robot, starting_positions):

    # find the gripper between the actuators and check if its state changed
    gripper = next(filter(lambda _: isinstance(_, Gripper), robot.motors))

    if not gripper.state_changed:
        return

    objects = [robot.getFromDef(f'P{i}') for i in range(24)]

    # if the gripper just closed, check if it caught something
    if gripper.close and on_plate(robot):

        # find the catchable objects (hardcoded quantity) and get the possibly first element that the robot faces
        prey_index = next((i for i in range(24) if is_above(robot, objects[i])), -1)

        if prey_index == -1:
            return

        # temporary remove the object from the environment (captured)
        objects[prey_index].getField('translation').setSFVec3f([0, -100, 0])

        # memorize the capture
        gripper.prey_index = prey_index

    # if it opens the grip while it is carrying a catchable, release it
    if not gripper.close and gripper.prey_index >= 0:

        # if robot is on the nest, reset the object position to its origin
        # otherwise, free the prey in the robot position
        rx, _, ry = robot.getFromDef('evolvable').getPosition()

        position = starting_positions[gripper.prey_index] if on_nest(robot) else [rx, 0.001, ry]
        objects[gripper.prey_index].getField('translation').setSFVec3f(position)

        gripper.prey_index = -1


def is_above(robot, obj) -> bool:
    rx, _, ry = robot.getFromDef('evolvable').getPosition()
    ox, _, oy = obj.getPosition()

    distance = sqrt((rx - ox) ** 2 + (ry - oy) ** 2)

    return distance <= 0.075 + 0.037
