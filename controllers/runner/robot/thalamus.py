from dataclasses import dataclass, field
from nanowire_network_simulator import minimum_distance_selection
from nanowire_network_simulator import mutate, random_nodes
from random import gauss
from robot.cortex import Cortex
from robot.body import EPuck
from robot.fiber import Fiber, nodes
from robot.pyramid import Pyramid


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

    # sensor/input signal attenuation. This represents the speculated property
    # of the thalamus to work as a low-pass filter and thus to perform some kind
    # of pre-processing. In the given system, it represents a dampening/
    # attenuation of the input signal.
    # A value of 0 means that the signal is directly forwarded to the node of
    # the network. An higher value cause the input signal to be lowered in its
    # intensity. The value should be in the range [0-1] as to be easily
    # multiplied to the input value to get the attenuation.
    attenuation: float = 0.0


def random(body: EPuck, cortex: Cortex, pyramid: Pyramid) -> Thalamus:
    """Instantiate a random thalamus to connect the robot body to the brain."""

    # select sensors nodes from the available ones
    network, motors = cortex.network, set(nodes(pyramid.mapping))
    illegal = minimum_distance_selection(motors, 2, True)(network, [], -1)
    sensors = list(random_nodes(network, illegal, len(body.sensors)))

    # map nodes and transducers
    return Thalamus(dict(zip(body.sensors, sensors)))


def evolve_attenuation(parent: Thalamus) -> Thalamus:
    """
    Evolve the attenuation of the sensors' inputs. The evolution uses the
    gaussian mutation method.
    """

    attenuation = min(1.0, max(0.0, parent.attenuation + gauss(0, 0.2)))
    return Thalamus(parent.mapping, attenuation)


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
    return Thalamus(mapping, parent.attenuation)


def describe(instance: Thalamus):
    """Return a custom string representation of the object."""

    return str('Sensor signal attenuation: {:.0e}'.format(instance.attenuation))
