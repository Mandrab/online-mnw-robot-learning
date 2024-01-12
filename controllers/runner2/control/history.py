from control.controller import Controller
from control.interface import Interface
from control.tsetlin.state import State
from nnspy import nns
from typing import List


class History:

    # arrays where to memorize the performance and state values, the control, and the interface information
    performance_collection: List[float]
    state_collection: List[State.Type]
    interface_collection: List[Interface]

    def __init__(self, controller: Controller, index: int):
        self.initial_controller = controller
        self.controller_index = index
        self.performance_collection = []
        self.state_collection = []
        self.interface_collection = []

    def save_performance(self, performance: float):
        self.performance_collection.append(performance)

    def save_state(self, state: State.Type):
        self.state_collection.append(state)

    def save_interface(self, interface: Interface):
        new = nns.copy_interface(interface)
        new = Interface(
            sources_count=new.sources_count, sources_index=new.sources_index,
            grounds_count=new.grounds_count, grounds_index=new.grounds_index,
            loads_count=new.loads_count, loads_index=new.loads_index, loads_weight=new.loads_weight,
            mapping=interface.mapping.copy(), multipliers=interface.multipliers.copy()
        )
        self.interface_collection.append(new)
