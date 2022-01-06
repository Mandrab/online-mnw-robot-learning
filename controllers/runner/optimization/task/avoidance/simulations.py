from collections import Callable

from logger import logger
from optimization.individual import Individual
from random import random
from robot.robot import run
from world.manager import Manager
from typing import Iterable


UPDATE_TIME = 100


def supplier(
        objects: Iterable[str],
        force_in_arena: Callable[[float], float],
        dynamic: bool = False  # TODO
) -> Callable[[Individual, int], None]:
    """Returns a life management that can work with movable objects."""

    def live(instance: Individual, duration: int):
        """
        Evaluate the individual in the t-maze task. Run a step of the robot and
        collect its result/fitness in it. Periodically run the task again with
        random selected side to reach (defined by starting floor color)
        """

        # save the manager of the world
        world_manager = Manager(instance.body, 'evolvable')
        multiplier, delta = 0.005, [[0, 0, 0] for _ in range(6)]

        # iterate for the epoch duration
        for counter in range(duration):

            # get object position and update them
            positions = filter(None, map(world_manager.position, objects))

            # update object directions
            if not counter % UPDATE_TIME:
                delta = [[random() - 0.5, 0, random() - 0.5] for _ in range(6)]
                delta = [[_ * multiplier for _ in p] for p in delta]

            if dynamic:
                for a, p, d in zip(objects, positions, delta):
                    new_p = [*map(force_in_arena, map(sum, zip(p, d)))]
                    world_manager.move(a, new_p, can_intersect=False)
                world_manager.commit(ensure=True)

            stimulus, response = run(instance)
            instance.biography.evaluator.update()
            instance.biography.stimulus.append(stimulus)
            instance.biography.response.append(response)

        logger.info(f'fitness: {instance.biography.evaluator.value()}')

    return live
