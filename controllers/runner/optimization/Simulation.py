from dataclasses import dataclass
from optimization.individual import Individual
from optimization.task.Task import Task


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


def update_elite(elite: Individual, instance: Simulation) -> Simulation:
    """Update a previous simulation with a new elite individual."""

    return Simulation(
        elite, instance.goal_task,
        instance.epochs_count, instance.epoch_duration,
        instance.evolution_threshold
    )
