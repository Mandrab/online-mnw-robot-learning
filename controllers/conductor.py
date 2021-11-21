from dataclasses import dataclass, field
from nanowire_network_simulator import stimulate
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from typing import Set, Dict


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

        inputs = [(self.mapping[pin], value) for pin, value in stimulus.items()]
        outputs = [
            (self.mapping[pin], actuators_resistance)
            for pin in self.actuators
        ]

        stimulate(
            self.network,
            self.datasheet,
            update_time,
            inputs,
            outputs,
            set()
        )

        return dict([
            (a, self.network.nodes[self.mapping[a]]['V'])
            for a in self.actuators]
        )
