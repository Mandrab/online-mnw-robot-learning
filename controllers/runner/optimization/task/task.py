from dataclasses import dataclass
from optimization.fitness import Fitness
from optimization.individual import Individual
from robot.body import EPuck
from typing import Callable, Tuple


@dataclass(frozen=True)
class Task:
    """Group the task configurations and utils."""

    life_manager: Callable[[Individual, int], None]
    evaluator: Callable[[EPuck], Fitness]
    sensors: Tuple[str]
