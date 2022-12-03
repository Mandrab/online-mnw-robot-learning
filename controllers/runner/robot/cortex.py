from dataclasses import dataclass, field
from nanowire_network_simulator import minimum_viable_network
from nanowire_network_simulator import initialize_graph_attributes
from nanowire_network_simulator import voltage_initialization
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from typing import Dict, Tuple


@dataclass(frozen=True)
class Cortex:
    """
    It's a wrapper for the device/controller and represents the reasoning area
    (or 'brain') of the robot. When provided with correct information, it
    creates a graceful interface to the more hardware-oriented logic of the
    device.
    """

    # graphs information and instance
    network: Graph
    datasheet: Datasheet
    wires: Dict = field(default_factory=dict)

    # accepted stimulus range of the network
    working_range: Tuple[float, float] = (0.0, 10.0)


def new(datasheet: Datasheet) -> Cortex:
    """Get a device represented by the given datasheet and initialize it."""

    graph, wires = minimum_viable_network(datasheet)
    initialize_graph_attributes(graph, set(), set(), datasheet.Y_min)
    voltage_initialization(graph, {next(iter(graph.nodes))}, set())
    return Cortex(graph, datasheet, wires)


def describe(instance: Cortex):
    """Return a custom string representation of the object."""

    graph, data = instance.network, instance.datasheet
    area = data.Lx * data.Ly
    d = data.wires_count * data.mean_length ** 2 / area
    cc_d = graph.number_of_nodes() * data.mean_length ** 2 / area
    wc = graph.number_of_nodes()
    jc = instance.network.number_of_edges()

    return str(f'Device density: {d}, CC density: {cc_d}, CC #wires: {wc}, CC #junctions: {jc}')
