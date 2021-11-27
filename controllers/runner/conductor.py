from dataclasses import dataclass, field
from nanowire_network_simulator import *
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from typing import Dict, Tuple
from utils import adapt

NETWORK_RANGE: Tuple[float, float] = (0, 10.0)


@dataclass
class Conductor:
    """
    Represents the controller of the robot.
    It manages the interconnections between the robot and the network,
    creating a graceful interface for their interaction.
    """

    network: Graph
    datasheet: Datasheet
    sensors: Dict[str, int] = field(default_factory=set)
    actuators: Dict[str, int] = field(default_factory=set)

    def set_sensors(self, sensors: Dict[str, int]):
        """
        Connect sensors to the network.
        The mapping represent the sensor/network-node mapping.
        """
        self.sensors = sensors

    def set_actuators(self, actuators: Dict[str, int]):
        """
        Connect actuators to the network
        The mapping represent the sensor/network-node mapping.
        """
        self.actuators = actuators

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
            stimulus: Dict[str, float],
            stimulus_range: Tuple[float, float],
            outputs_range: Tuple[float, float],
            actuators_resistance: float = 1
    ) -> dict[str, float]:
        """
        Stimulate the network with the sensors signals.
        Evaluate its response and return it.
        """

        # get used sensors
        stimulus = filter(lambda p: p[0] in self.sensors, stimulus.items())

        # get sensors readings
        stimulus = [(self.sensors[sensor], value) for sensor, value in stimulus]

        # remap sensors readings from their range to 0, 10 (voltages)
        stimulus = [
            (k, adapt(v, stimulus_range, NETWORK_RANGE))
            for k, v in stimulus
        ]
        # print('in voltages:\t', stimulus)

        # define the pin-resistance/load pairs for the motors
        outputs = [
            (self.actuators[pin], actuators_resistance)
            for pin in self.actuators
        ]

        # stimulate the network with the sensors inputs
        stimulate(
            graph=self.network,
            datasheet=self.datasheet,
            delta_time=update_time,
            inputs=stimulus,
            outputs=outputs,
            grounds=set()
        )

        # extract outputs from network
        outputs = [
            (a, self.network.nodes[self.actuators[a]]['V'])
            for a in self.actuators
        ]
        print('out voltages:\t', {s: p[0] for s, p in zip(['l', 'r'], outputs)})

        # remap output value from 0, 10 to -6.28, 6.28 todo
        return {k: -adapt(v, NETWORK_RANGE, outputs_range) for k, v in outputs}
