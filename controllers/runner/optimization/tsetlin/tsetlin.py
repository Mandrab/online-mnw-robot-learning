from __future__ import annotations
from logger import logger
from optimization.tsetlin.state import State, str2phase
from typing import List

import json


class Tsetlin:
    states: List[State]  # states list

    state_idx: int  # current state index
    start_idx: int  # starting state index

    stagnation_tolerance: float

    def __init__(self, design_path: str = "../../tsetlin.json"):

        # open and load the Tsetlin configuration
        with open(design_path) as file:
            data = json.load(file)

        # create the required number of states
        self.states = [State() for _ in range(
            len(data["exploration"]) +
            len(data["operation"]) +
            len(data["adaptation"])
        )]

        # set up the tsetlin main state, current state and its stagnation tolerance
        self.start_idx = self.state_idx = data["main_state"]
        self.stagnation_tolerance = data["stagnation_tolerance"]

        # maintain only the states information
        del data["main_state"]
        del data["stagnation_tolerance"]

        # set up the Tsetlin states
        for phase, states in data.items():
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
