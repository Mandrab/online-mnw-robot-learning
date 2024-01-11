import random

from dataclasses import dataclass
from functools import reduce
from logger import logger
from optimization.individual import Individual, evolve, copy
from optimization.task.task import Task
from optimization.tsetlin.state import State
from optimization.tsetlin.tsetlin import Tsetlin
from robot.robot import describe
from typing import Any, Tuple


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
    tsetlin: Tsetlin


def optimize(instance: Simulation) -> Simulation:
    """
    Optimize a static robot configuration (body + cortex) through the run of a
    simulation of individuals with different thalamus (the changing part).
    In other words, find the best thalamus to connect body and cortex in order
    to achieve the desired task.
    """

    logger.info(describe(instance.elite))

    # set controller random seed
    random.seed(instance.elite.cortex.datasheet.generation_seed)

    # restore simulation to starting point
    instance.elite.body.simulationReset()

    # run the initial individual to obtain its fitness
    instance.goal_task.life_manager(instance.elite, instance.epoch_duration)

    def strategy(individuals: Tuple[Individual, Individual], _: Any) -> Tuple[Individual, Individual]:
        """
        Reduction strategy. Given the best individual and the previously tested
        one, generate an adapted version of the controller and compare it with
        the previous best known one. The new controller can be adapted from the
        best one, or from the last tested if in exploration mode. Keep the one
        with the highest score. If the tsetlin machine is in operation mode,
        the best controller is used without being adapted.
        """

        elite, challenger = individuals

        # get the challenger individual (may or not be an evolution of elite)
        task = instance.goal_task
        evaluator = task.evaluator(elite.body)
        threshold, sigma = task.evolution_threshold, task.mutation_sigma

        instance.tsetlin.transit(challenger.biography.evaluator.value(), elite.biography.evaluator.value())

        # adaptation mode
        if instance.tsetlin.state == State.Type.ADAPTATION:
            challenger = evolve(elite, threshold, sigma, evaluator)
        # exploration mode
        elif instance.tsetlin.state == State.Type.EXPLORATION:
            challenger = evolve(challenger, threshold, sigma, evaluator)
        # operation mode
        else:
            challenger = copy(elite, evaluator)

        # restore simulation to starting point
        if not task.continuous:
            challenger.body.simulationReset()

        # run the challenger to obtain its fitness
        instance.goal_task.life_manager(challenger, instance.epoch_duration)

        return (challenger if challenger.fitness >= elite.fitness else elite), challenger

    # find the best configuration in the given task and world
    winner = reduce(strategy, range(instance.epochs_count), (instance.elite, instance.elite))[0]
    return update_elite(winner, instance)


def update_elite(elite: Individual, instance: Simulation) -> Simulation:
    """Update a previous simulation with a new elite individual."""

    return Simulation(
        elite,
        instance.goal_task,
        instance.epochs_count,
        instance.epoch_duration,
        instance.tsetlin
    )
