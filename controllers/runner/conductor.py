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

    # accepted stimulus range of the network
    stimulus_range: Tuple[float, float] = (0.0, 10.0)

    # mappings that represent the sensor/actuator -> network-node relation
    sensors: Dict[str, int] = field(default_factory=dict)
    actuators: Dict[str, int] = field(default_factory=dict)

    def initialize(self):
        """Initialize network"""
        initialize_graph_attributes(
            graph=self.network,
            sources={*self.sensors.values()},
            grounds=set(),
            y_in=self.datasheet.Y_min
        )
        voltage_initialization(self.network, {*self.sensors.values()}, set())

    def evaluate(
            self,
            update_time: float,
            inputs: Dict[str, float],
            inputs_range: Tuple[float, float],
            outputs_range: Tuple[float, float],
            actuators_load: float = 1
    ) -> dict[str, float]:
        """
        Stimulate the network with the sensors signals.
        Evaluate its response and return it.
        """
        # filter to get used sensors
        inputs = [(k, v) for k, v in inputs.items() if k in self.sensors]

        # get sensors readings
        inputs = [(self.sensors[k], v) for k, v in inputs]

        # remap sensors readings from their range to network range (voltages)
        inputs = [
            (k, adapt(v, inputs_range, self.stimulus_range))
            for k, v in inputs
        ]
        # print('in voltages:\t', inputs)

        # define the pin-resistance/load pairs for the motors
        outputs = [(pin, actuators_load) for pin in self.actuators.values()]

        # stimulate the network with the sensors inputs
        stimulate(
            graph=self.network,
            datasheet=self.datasheet,
            delta_time=update_time,
            inputs=inputs,
            outputs=outputs,
            grounds=set()
        )

        # extract outputs from network
        outputs = [
            (actuator, self.network.nodes[pin]['V'])
            for actuator, pin in self.actuators.items()
        ]
        # print('out voltages:\t', {s: p[1] for s, p in zip(['l', 'r'], outputs)})

        # remap output values from 0, 10 to:
        #   -6.28, 6.28 for distance: 10 = far -> 6.28 = move straight
        #   6.28, -6.28 for proximity: 10 = near -> -6.28 = go away
        return {
            k: adapt(v, self.stimulus_range, outputs_range)
            for k, v in outputs
        }
