import random

from logger import logger
from optimization.individual import Individual
from robot.robot import run
from world.Colors import Colors
from world.Manager import Manager

DURATION = 200

INITIAL_POSITION = [0, 3e-5, 0.8]
INITIAL_ROTATION = [0, -1, 0, 0]

BLACK_START = Colors.BLACK, [0, 2e-5, 0.4], [0, -1, 0.4]
WHITE_START = Colors.WHITE, [0, -1, 0.4], [0, 2e-5, 0.4]


def live(instance: Individual, duration: int):
    """
    Evaluate the individual in the t-maze task. Run a step of the robot and
    collect its result/fitness in it. Periodically run the task again with
    random selected side to reach (defined by starting floor color)
    """

    # save the manager of the world
    world_manager = Manager(instance.body, 'evolvable')

    # iterate for the epoch duration
    for counter in range(duration):
        if not counter % DURATION:

            # reset robot to start position
            world_manager.move('evolvable', INITIAL_POSITION)
            world_manager.rotate('evolvable', INITIAL_ROTATION)

            # ensure that changes take place
            world_manager.commit()

            # randomly set a floor as starting one (basically, hide the other)
            starting_color, black_position, white_position = BLACK_START
            if random.randint(0, 1):
                starting_color, black_position, white_position = WHITE_START
            world_manager.move('light_floor', white_position)
            world_manager.move('dark_floor', black_position)

            # (re)set initial color of evaluator utils
            instance.biography.evaluator.initial_color = starting_color

        stimulus, response = run(instance)
        instance.biography.evaluator.update()
        instance.biography.stimulus.append(stimulus)
        instance.biography.response.append(response)

    logger.info('fitness: ' + str(instance.biography.evaluator.value()))
