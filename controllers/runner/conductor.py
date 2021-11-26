import operator

from dataclasses import dataclass, field
from functools import reduce
from nanowire_network_simulator import *
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from typing import Set, Dict, Tuple

# todo in reality (0.0, 4095.0), but it basically never reach those values
SENSOR_RANGE: Tuple[float, float] = (0.0, 1500)  # (0.0, 7.0)
MOTOR_RANGE: Tuple[float, float] = (-6.28, 6.28) # (-6.28, 6.28)


@dataclass
class Conductor:
    """
    Represents the controller of the robot.
    It manages the interconnections between the robot and the network,
    creating a graceful interface for their interaction.
    """

    network: Graph
    datasheet: Datasheet
    sensors: Set[str] = field(default_factory=set)
    actuators: Set[str] = field(default_factory=set)
    mapping: Dict[str, int] = field(default_factory=dict)

    def set_sensors(
            self,
            sensors: Set[str],
            mapping: Dict[str, int] = field(default_factory=dict)
    ):
        """
        Connect sensors to the network
        The mapping represent the sensor/network-node mapping.
        In case of redefinition of a mapping, the new one is taken.
        """

        self.sensors = sensors
        self.mapping |= mapping

    def set_actuators(
            self,
            actuators: Set[str],
            mapping: Dict[str, int] = field(default_factory=dict)
    ):
        """
        Connect actuators to the network
        The mapping represent the sensor/network-node mapping.
        In case of redefinition of a mapping, the new one is taken.
        """

        self.actuators = actuators
        self.mapping |= mapping

    def initialize(self):
        """Initialize network"""
        sources = {self.mapping[s] for s in self.sensors}
        initialize_graph_attributes(
            graph=self.network,
            sources=sources,
            grounds=set(),
            y_in=self.datasheet.Y_min
        )
        voltage_initialization(self.network, sources, set())

    def evaluate(
            self,
            update_time: float,
            stimulus: dict[str, float],
            actuators_resistance: float = 1
    ) -> dict[str, float]:
        """
        Stimulate the network with the sensors signals.
        Evaluate its response and return it.
        """

        # get used sensors
        stimulus = filter(lambda p: p[0] in self.sensors, stimulus.items())

        # get sensors readings
        stimulus = [(self.mapping[sensor], value) for sensor, value in stimulus]

        # remap sensors readings from their range to 0, 10 (voltages)
        stimulus = [(k, adapt(v, SENSOR_RANGE, (0, 10))) for k, v in stimulus]
        # print('in voltages:\t', stimulus)

        # define the pin-resistance/load pairs for the motors
        outputs = [
            (self.mapping[pin], actuators_resistance)
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
            (a, self.network.nodes[self.mapping[a]]['V'])
            for a in self.actuators
        ]
        # print('out voltages:\t', {s: v for s,(k,v) in zip(['l', 'r'], outputs)})
        # remap output value from 0, 10 to -6.28, 6.28
        return {k: -adapt(v, (0, 10), MOTOR_RANGE) for k, v in outputs}  # todo


def adapt(
        value: float,
        in_range: Tuple[float, float],
        out_range: Tuple[float, float]
) -> float:
    """Adapt a value to a different range"""

    in_delta = reduce(operator.__sub__, reversed(in_range))
    out_delta = reduce(operator.__sub__, reversed(out_range))
    value = out_range[0] + (value - in_range[0]) * out_delta / in_delta

    # force bounds to the value
    value = min(value, out_range[1])
    value = max(value, out_range[0])

    return value
