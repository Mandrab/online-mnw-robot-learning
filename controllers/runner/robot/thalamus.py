from dataclasses import dataclass, field
from math import ceil
from random import gauss, sample, randrange, choice
from robot.cortex import Cortex
from robot.body import EPuck
from robot.fiber import Fiber, nodes
from robot.pyramid import Pyramid
from typing import Dict
from util.evolutor import minimum_distance_selection


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
    # the network. A higher value cause the input signal to be increased in its
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

    # select the nodes that are at least 2 junctions far from the motor nodes
    component, motors = cortex.component, set(nodes(pyramid.mapping))
    motors = {
        m - component.ws_skip
        for m in motors
        if component.ws_skip <= m < component.ws_skip + component.ws_count
    }
    legal_nodes = minimum_distance_selection(component, motors, 2)
    legal_nodes = [component.ws_skip + idx for idx in legal_nodes]

    # select some nodes to be used as sensor inputs
    sensors = sample(legal_nodes, len(body.sensors))
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
    sensor-to-node connections. The function reconnects a minimum of 1 node
    to a maximum of 50% of the nodes.
    """

    # select the nodes to reconnect
    sensors_count = len(parent.mapping)
    reconnections_count = randrange(1, ceil(sensors_count * 0.5))
    connections = sample(parent.mapping.items(), reconnections_count)

    # select the nodes that are at least 2 junctions far from the motor nodes
    component, motors = cortex.component, set(nodes(pyramid.mapping))
    motors = {
        m - component.ws_skip
        for m in motors
        if component.ws_skip <= m < component.ws_skip + component.ws_count
    }
    legal_nodes = minimum_distance_selection(component, motors, 2)
    legal_nodes = [component.ws_skip + idx for idx in legal_nodes]

    # reconnect each sensor to a different node
    def reconnect(pair): return pair[0], choice(list(legal_nodes - {pair[1]}))
    connections = dict(map(reconnect, connections))

    return Thalamus(parent.mapping | connections, parent.multiplier)


def describe(instance: Thalamus) -> str:
    """Return a custom string representation of the object."""

    average = sum(instance.multiplier.values()) / len(instance.multiplier)
    return f'Average sensor signal multiplication: {average * 100}%'
