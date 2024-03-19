from __future__ import annotations
from control.tsetlin.state import State, str2phase
from inout.logger import logger
from inout.loader import tsetlin_configs
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
        self.stagnation_tolerance_bottom = tsetlin_configs["stagnation_tolerance_bottom"]
        self.stagnation_tolerance_up = tsetlin_configs["stagnation_tolerance_up"]

        # set up the Tsetlin states
        for phase, states in filter(
                lambda x: x[0] in ["exploration", "operation", "adaptation"],
                tsetlin_configs.items()
        ):
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

        # calculate the upper and lower bound for stagnation
        lower_stagnation = best_performance - self.stagnation_tolerance_bottom
        upper_stagnation = best_performance + self.stagnation_tolerance_up

        # if the performance is stagnating performs a stagnation transition
        if lower_stagnation <= last_performance <= upper_stagnation:
            self.state_idx = self.state.transition[State.Transition.PERFORMANCE_STAGNATION]
        # if the last performance is greater than the best, it is an improvement
        elif last_performance > best_performance:
            self.state_idx = self.state.transition[State.Transition.PERFORMANCE_INCREASE]
        # if the performance is decreasing performs a decrease transition
        else:
            self.state_idx = self.state.transition[State.Transition.PERFORMANCE_DECREASE]

        # log the new reached state
        logger.info(f"new phase: {self.state.type} (idx: {self.state_idx})")


__all__ = "Tsetlin",