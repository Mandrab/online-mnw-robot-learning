from logger import logger
from math import sin, cos
from optimization.individual import Individual
from optimization.task.foraging.gripper import Gripper
from optimization.task.foraging.util import is_facing
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
    ground_sensor = next(filter(lambda _: _.startswith('gs0'), robot.sensors))

    if not gripper.state_changed:
        return

    # if the gripper just closed, check if it caught something
    if gripper.close:

        # find the catchable objects (hardcoded quantity) and get the possibly first element that the robot faces
        objects = [robot.getFromDef(f'c{i}') for i in range(24)]
        prey = next(filter(lambda _: is_facing(robot, _), objects), None)

        if prey is not None:
            # temporary remove the object from the environment (captured)
            position = prey.getField('translation').getSFVec3f()
            prey.getField('translation').setSFVec3f([0, -100, 0])

            # memorize the capture
            gripper.prey = (prey, position)

    # if it opens the grip while it is carrying a catchable, release it
    elif gripper.prey is not None:

        # calculate if the robot is on the nest
        on_nest = ground_sensor.value < 500

        # if robot is on the nest, reset the object position to its origin
        if on_nest:
            gripper.prey[0].getField('translation').setSFVec3f(gripper.prey[1])

        # free the prey in the position immediately ahead the robot
        else:
            # get actual position and rotation of the robot
            x, y, z = robot.getFromDef('evolvable').getPosition()
            _, a, _, b = robot.getFromDef('evolvable').getField('rotation').getSFRotation()

            x -= .075 * sin(a * b)
            z -= .075 * cos(a * b)

            gripper.prey[0].getField('translation').setSFVec3f([x, y, z])

        gripper.prey = None
