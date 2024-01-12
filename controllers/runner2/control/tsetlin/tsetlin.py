from __future__ import annotations
from inout.logger import logger
from inout.loader import tsetlin_configs
from control.tsetlin.state import State, str2phase
from typing import List


class Tsetlin:

    states: List[State]  # states list

    state_idx: int  # current state index
    start_idx: int  # starting state index

    stagnation_tolerance: float

    def __init__(self):

        # create the required number of states
        self.states = [State() for _ in range(
            len(tsetlin_configs["exploration"]) +
            len(tsetlin_configs["operation"]) +
            len(tsetlin_configs["adaptation"])
        )]

        # set up the tsetlin main state, current state and its stagnation tolerance
        self.start_idx = self.state_idx = tsetlin_configs["main_state"]
        self.stagnation_tolerance = tsetlin_configs["stagnation_tolerance"]

        # maintain only the states information
        del tsetlin_configs["main_state"]
        del tsetlin_configs["stagnation_tolerance"]

        # set up the Tsetlin states
        for phase, states in tsetlin_configs.items():
            for state in states:
                self.states[state["id"]].type = str2phase(phase)
                self.states[state["id"]].transition = {
                    State.Transition.PERFORMANCE_INCREASE: state["performance-increase"],
                    State.Transition.PERFORMANCE_DECREASE: state["performance-decrease"],
                    State.Transition.PERFORMANCE_STAGNATION: state["performance-stagnation"]
                }

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
        logger.info(f"new phase: {self.state.type}")
