from control.coupling import Coupling
from control.tsetlin.state import State
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Adaptation:
    configuration: Coupling     # a tested control configuration
    tsetlin_state: State.Type   # the tsetlin state when the configuration was created
    tsetlin_index: int          # memorize the index of the tsetlin state


class History(List[Adaptation]):

    best_configuration: Coupling

    def __init__(self, configuration: Coupling):
        super().__init__()
        self.best_configuration = configuration


__all__ = "Adaptation", "History"
