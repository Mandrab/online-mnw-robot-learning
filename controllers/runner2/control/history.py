from control.controller import Controller
from control.interface import Interface
from control.tsetlin.state import State
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class History:

    # arrays where to memorize the control, the interface, the performance and state values
    initial_controller: Controller
    controller_index: int
    performance_collection: List[float]
    state_collection: List[State.Type]
    interface_collection: List[Interface]

    def save_performance(self, performance: float):
        self.performance_collection.append(performance)

    def save_state(self, state: State.Type):
        self.state_collection.append(state)

    def save_interface(self, interface: Interface):
        self.interface_collection.append(interface.copy())


def history(controller: Controller, index: int):
    return History(controller, index, [], [], [])
