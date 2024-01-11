from __future__ import annotations
from optimization.tsetlin.state import State
from typing import List


class Tsetlin:

    states: List[State]             # states list
    state_idx: int                  # current state index
    start_idx: int                  # starting state index
    stagnation_tolerance: float

    def __init__(self, states_count: int):
        self.states = [State() for _ in range(states_count)]

    @property
    def state(self) -> State:
        return self.states[self.state_idx]

    def transit(self, last_performance: float, best_performance: float):
        if best_performance < last_performance:
            self.state_idx = self.state.transition[State.Transition.PERFORMANCE_INCREASE]
        elif abs(best_performance - last_performance) < self.stagnation_tolerance:
            self.state_idx = self.state.transition[State.Transition.PERFORMANCE_STAGNATION]
        else:
            self.state_idx = self.state.transition[State.Transition.PERFORMANCE_DECREASE]

    def reset(self) -> Tsetlin:
        self.state_idx = self.start_idx
        return self
