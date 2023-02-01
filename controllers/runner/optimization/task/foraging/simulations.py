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

    # iterate for the epoch duration
    for counter in range(duration):

        # run the individual
        stimulus, response = run(instance)

        # evaluate the actions
        instance.biography.evaluator.update()

        # correct world state
        update_world(instance.body)

        # save the biography for the step
        instance.biography.stimulus.append(stimulus)
        instance.biography.response.append(response)

        logger.cortex_plot(instance)

    logger.info('fitness: ' + str(instance.biography.evaluator.value()))


def update_world(robot):

    # find the gripper between the actuators and check if its state changed
    gripper = next(filter(lambda _: isinstance(_, Gripper), robot.motors))

    if not gripper.state_changed:
        return

    # if the gripper just closed, check if it caught something
    if gripper.close and on_plate(robot):

        # find the catchable objects (hardcoded quantity) and get the possibly first element that the robot faces
        objects = [robot.getFromDef(f'P{i}') for i in range(24)]
        prey = next(filter(lambda _: is_above(robot, _), objects), None)

        if prey is None:
            return

        # temporary remove the object from the environment (captured)
        position = prey.getField('translation').getSFVec3f()
        prey.getField('translation').setSFVec3f([0, -100, 0])

        # memorize the capture
        gripper.prey = (prey, position)

    # if it opens the grip while it is carrying a catchable, release it
    elif gripper.prey is not None:

        # if robot is on the nest, reset the object position to its origin
        # otherwise, free the prey in the robot position
        prey, original_position = gripper.prey
        rx, _, ry = robot.getFromDef('evolvable').getPosition()

        position = original_position if on_nest(robot) else [rx, 0.001, ry]
        prey.getField('translation').setSFVec3f(position)

        gripper.prey = None


def is_above(robot, obj) -> bool:
    rx, _, ry = robot.getFromDef('evolvable').getPosition()
    ox, _, oy = obj.getPosition()

    distance = sqrt((rx - ox) ** 2 + (ry - oy) ** 2)

    return distance <= 0.075 + 0.037
