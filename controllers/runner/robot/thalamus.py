from dataclasses import dataclass, field
from nanowire_network_simulator import minimum_distance_selection
from nanowire_network_simulator import mutate, random_nodes
from random import gauss
from robot.cortex import Cortex
from robot.body import EPuck
from robot.fiber import Fiber, nodes
from robot.pyramid import Pyramid
from typing import Dict


@dataclass(frozen=True)
class Thalamus:
    """
    Relay the sensory information from the body sensors to the brain. In the
    context of the epuck, it connects the receptors/actuators to randomly chosen
    nodes of the brain (i.e., the network). It also performs some basic
    pre-processing of the signal, possibly attenuating it.
    """

    # mappings that represents the sensors -> network-nodes relation
    mapping: Fiber = field(default_factory=dict)

    # sensor/input signal multiplier. This represents the speculated property
    # of the thalamus to work as a low-pass filter and thus to perform some kind
    # of pre-processing. In the given system, this elaboration is represented as
    # a multiplication of the input signal.
    # A value of 1 means that the signal is directly forwarded to the node of
    # the network. An higher value cause the input signal to be increased in its
    # intensity. The minimum value is 0, for which the signal is inhibited.
    multiplier: Dict[str, float] = field(default_factory=dict)


def random(
        body: EPuck,
        cortex: Cortex,
        pyramid: Pyramid,
        sigma: float = 0.3
) -> Thalamus:
    """
    Instantiate a random thalamus to connect the robot body to the brain. The
    sensor multiplier is randomly chosen through use of a wide gaussian. The
    default and suggested sigma is 0.3 for collision avoidance and t-maze tasks,
    while ~2.5 for area avoidance (it needs the sensor to highly stimulate).
    """

    # select sensors nodes from the available ones
    network, motors = cortex.network, set(nodes(pyramid.mapping))
    illegal = minimum_distance_selection(motors, 2, True)(network, [], -1)
    sensors = list(random_nodes(network, illegal, len(body.sensors)))
    multiplier = {s: abs(gauss(1, sigma)) for s in body.sensors}

    # map nodes and transducers
    return Thalamus(dict(zip(body.sensors, sensors)), multiplier)


def evolve_multiplier(parent: Thalamus, sigma: float = 0.1) -> Thalamus:
    """
    Evolve the multiplier of the sensors' inputs. The evolution uses the
    gaussian mutation method. The default and suggested sigma is 0.1 for
    collision avoidance and t-maze tasks, while ~1.0 for area avoidance (it
    needs the sensor to highly stimulate the network).
    """

    def update(value: float) -> float: return max(0.0, value + gauss(0, sigma))
    multiplier = dict((k, update(v)) for k, v in parent.multiplier.items())

    return Thalamus(parent.mapping, multiplier)


def evolve_connections(
        cortex: Cortex,
        pyramid: Pyramid,
        parent: Thalamus
) -> Thalamus:
    """
    Evolve the given thalamus to a new one originated from it, changing its
    sensor-to-node connections.
    """

    # obtain the new sensors
    selector = minimum_distance_selection({*nodes(pyramid.mapping)}, distance=2)
    mapping = dict(zip(parent.mapping, mutate(
        cortex.network,
        list(nodes(parent.mapping)), ground=-1,
        probability=0.3, minimum_mutants=1, maximum_mutants=4,
        viable_node_selection=selector
    )))
    return Thalamus(mapping, parent.multiplier)


def describe(instance: Thalamus) -> str:
    """Return a custom string representation of the object."""

    average = sum(instance.multiplier.values()) / len(instance.multiplier)
    return f'Average sensor signal multiplication: {average * 100}%'
