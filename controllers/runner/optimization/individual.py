from dataclasses import dataclass
from logger import logger
from optimization.fitness import Fitness
from optimization.biography import Biography
from robot.robot import Robot, run, unroll
from robot.thalamus import evolve_connections, evolve_attenuation, random


@dataclass(frozen=True)
class Individual(Robot):
    """
    It represents a configuration that has been, or is going to be, evaluated in
    the context of the evolution of a population. It stores the 'memory' of the
    robot defined as the stimulus and response that he got from the environment,
    as well as the overall score that he got in it.
    """

    biography: Biography

    @property
    def fitness(self): return self.biography.evaluator.value()


def live(individual: Individual, duration: int):
    """Evaluate the individual in the given task."""

    # iterate for the epoch duration
    for _ in range(duration):

        # run the individual and save the biography for the step
        stimulus, response = run(individual)
        individual.biography.evaluator.update()
        individual.biography.stimulus.append(stimulus)
        individual.biography.response.append(response)

        logger.cortex_plot(individual)

    logger.info(f'fitness: {individual.biography.evaluator.value()}')


def evolve(
        parent: Individual,
        evolution_threshold: float,
        evaluator: Fitness
) -> Individual:
    """
    If enough strong (fitness), generate and individual from the given one,
    otherwise generate a random new one.
    """

    body, cortex, pyramid, thalamus = unroll(parent)
    if parent.fitness >= evolution_threshold:
        thalamus = evolve_connections(cortex, pyramid, thalamus)
        thalamus = evolve_attenuation(thalamus)
    else:
        thalamus = random(body, cortex, pyramid)
    return Individual(body, cortex, pyramid, thalamus, Biography(evaluator))
