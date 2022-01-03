import dataclasses

from dataclasses import dataclass, field
from nanowire_network_simulator import *
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from typing import Dict, Tuple
from utils import adapt


@dataclass
class Conductor:
    """
    Represents the controller of the robot.
    It manages the interconnections between the robot and the network,
    creating a graceful interface for their interaction.
    """

    # graphs information and instance
    network: Graph
    datasheet: Datasheet
    wires: Dict = field(default_factory=dict)

    # accepted stimulus range of the network
    network_range: Tuple[float, float] = (0.0, 10.0)

    # mappings that represent the sensor/actuator -> network-node relation
    sensors: Dict[str, int] = field(default_factory=dict)
    actuators: Dict[str, int] = field(default_factory=dict)

    # motors/actuators load
    load: float = 1e6   # MOhm

    def initialize(self):
        """Initialize network setting voltages values to nodes."""

        initialize_graph_attributes(
            graph=self.network,
            sources=set(self.sensors.values()),
            grounds=set(),
            y_in=self.datasheet.Y_min
        )
        voltage_initialization(self.network, {*self.sensors.values()}, set())

    def evaluate(
            self,
            delta_time: float,
            inputs: Dict[str, float],
            inputs_range: Tuple[float, float] = (0.0, 1.0),
            outputs_range: Tuple[float, float] = (0.0, 1.0)
    ) -> Dict[str, float]:
        """
        Stimulate the network with the sensors signals.
        Evaluate its response and return it.
        """

        # filter to get used sensors
        reads = [(k, v) for k, v in inputs.items() if k in self.sensors]

        # get sensors readings
        reads = [(self.sensors[k], v) for k, v in reads]

        # remap sensors readings from their range to network range (voltages)
        reads = [
            (k, adapt(v, inputs_range, self.network_range))
            for k, v in reads
        ]

        # define the pin-resistance/load pairs for the motors
        loads = [(pin, self.load) for pin in self.actuators.values()]

        # stimulate the network with the sensors inputs
        stimulate(self.network, self.datasheet, delta_time, reads, loads, set())

        # extract outputs from network
        outs = [
            (actuator, self.network.nodes[pin]['V'])
            for actuator, pin in self.actuators.items()
        ]

        # remap output values from 0, 10 to:
        #   -6.28, 6.28 for distance: 10 = far -> 6.28 = move straight
        #   6.28, -6.28 for proximity: 10 = near -> -6.28 = go away
        return {k: adapt(v, self.network_range, outputs_range) for k, v in outs}


def copy(conductor: Conductor) -> Conductor:
    """Create a deep copy of the conductor"""

    return Conductor(
        conductor.network.copy(),
        dataclasses.replace(conductor.datasheet),
        conductor.wires.copy(),
        conductor.network_range,
        conductor.sensors.copy(),
        conductor.actuators.copy(),
        conductor.load
    )
