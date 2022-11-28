from dataclasses import dataclass
from optimization.fitness import Fitness
from optimization.individual import Individual
from robot.body import EPuck
from typing import Callable


@dataclass(frozen=True)
class Task:
    """Group the task configurations and utils."""

    executor: Callable[[], EPuck]
    life_manager: Callable[[Individual, int], None]
    evaluator: Callable[[EPuck], Fitness]
    evolution_threshold: float
    creation_sigma: float
    mutation_sigma: float
    continuous: bool = True
