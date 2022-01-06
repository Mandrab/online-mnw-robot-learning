import random

from dataclasses import dataclass
from functools import reduce
from logger import logger
from optimization.individual import Individual, evolve
from optimization.task.Task import Task
from robot.robot import describe
from typing import Any


@dataclass(frozen=True)
class Simulation:
    """
    Codify the information needed for the evolution of an individual. Only the
    data of the best individual are maintained, while the others are discarded.
    Note that this class does not want to represent a step in the evolution,
    instead, it aims to define its starting or ending point. The step approach
    can be however obtained setting a epoch count and an epoch duration of 1.
    """

    elite: Individual
    goal_task: Task
    epochs_count: int
    epoch_duration: int
    evolution_threshold: float


def optimize(instance: Simulation) -> Simulation:
    """
    Optimize a static robot configuration (body + cortex) through the run of a
    simulation of individuals with different thalamus (the changing part).
    In other words, find the best thalamus to connect body and cortex in order
    to achieve the desired task.
    """

    logger.info(describe(instance.elite))

    # set controller random seed
    random.seed(instance.elite.cortex.datasheet.seed)

    def strategy(elite: Individual, _: Any) -> Individual:
        """
        Reduction strategy. Given an individual, it compares it with another one
        that may or not be its evolution. Select the one with the highest score.
        """

        # get the challenger individual (may or not be an evolution of elite)
        evaluator = instance.goal_task.evaluator(elite.body)
        challenger = evolve(elite, instance.evolution_threshold, evaluator)

        # restore simulation to starting point
        challenger.body.simulationReset()

        # run the challenger to obtain its fitness
        instance.goal_task.life_manager(challenger, instance.epoch_duration)

        return challenger if challenger.fitness >= elite.fitness else elite

    # find the best configuration in the given task and world
    winner = reduce(strategy, range(instance.epochs_count), instance.elite)
    return update_elite(winner, instance)


def update_elite(elite: Individual, instance: Simulation) -> Simulation:
    """Update a previous simulation with a new elite individual."""

    return Simulation(
        elite, instance.goal_task,
        instance.epochs_count, instance.epoch_duration,
        instance.evolution_threshold
    )
