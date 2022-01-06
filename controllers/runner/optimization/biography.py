from dataclasses import dataclass, field
from optimization.fitness import Fitness
from typing import List, Dict


@dataclass(frozen=True)
class Biography:
    """
    Summarize the life of an individual. It contains the fitness obtained and
    the history of the agent.
    """

    evaluator: Fitness
    stimulus: List[Dict[str, float]] = field(default_factory=list)
    response: List[Dict[str, float]] = field(default_factory=list)
