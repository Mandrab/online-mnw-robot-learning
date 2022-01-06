from dataclasses import dataclass, field
from nanowire_network_simulator import minimum_distance_selection
from nanowire_network_simulator import mutate, random_nodes
from robot.cortex import Cortex
from robot.body import EPuck
from typing import Dict


@dataclass(frozen=True)
class Thalamus:
    """
    Relay the sensory and command information between the brain and the body of
    the robot. In the context of the epuck, it connects the transducers to
    randomly chosen nodes of the brain (i.e., the network). For the actuators,
    it also specify their sensitivity that, in this context, is intended as
    their response to stimulation.
    """

    # mappings that represent the sensor/actuator -> network-node relation
    sensors: Dict[str, int] = field(default_factory=dict)
    motors: Dict[str, int] = field(default_factory=dict)

    # motors/actuators load. since higher values make the robot 'more active',
    # it can be seen as the sensitivity of a natural muscles
    sensitivity: float = 1e6   # MOhm


def random(cortex: Cortex, body: EPuck, load: float) -> Thalamus:
    """Instantiate a random thalamus to connect the robot body to the brain."""

    # select actuator and sensors nodes from the available ones
    motors = random_nodes(cortex.network, set(), len(body.motors))
    illegal = minimum_distance_selection(motors, 2, True)(cortex.network, [], -1)
    sensors = list(random_nodes(cortex.network, illegal, len(body.sensors)))

    # map nodes and transducers
    sensors = dict(zip(body.sensors, sensors))
    motors = dict(zip(body.motors, motors))
    return Thalamus(sensors, motors, load)


def evolve(cortex: Cortex, thalamus: Thalamus) -> Thalamus:
    """Evolve the given thalamus to a new one originated from it."""

    # obtain the new sensors
    ground, probability, minimum_mutants, maximum_mutants = -1, 0.3, 1, 4
    sensors = dict(zip(thalamus.sensors, mutate(
        cortex.network,
        list(thalamus.sensors.values()), ground,
        probability, minimum_mutants, maximum_mutants,
        minimum_distance_selection(set(thalamus.motors.values()), distance=2)
    )))

    return Thalamus(sensors, thalamus.motors, thalamus.sensitivity)


def describe(instance: Thalamus):
    """Return a custom string representation of the object."""

    return str('Motors load: {:.0e}'.format(instance.sensitivity))
