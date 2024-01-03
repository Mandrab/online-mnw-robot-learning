from dataclasses import dataclass, field
from random import gauss, sample
from robot.body import EPuck
from robot.cortex import Cortex
from robot.fiber import Fiber


@dataclass
class Pyramid:
    """
    The pyramid represents the descending motor pathways that originates in the
    cortex and descend to the motors. This abstraction helps to link between
    motor's nodes and network's node.
    """

    # mappings that represents the network-nodes -> motors relation
    mapping: Fiber = field(default_factory=dict)

    # motors/actuators load. Since higher values make the robot 'more active',
    # it can be seen as the sensitivity of natural muscles towards their input
    # signal. It has however to be noted that this comparison is not completely
    # coherent with the tested system, in that the load influences the signal
    # propagation inside the network. The default value corresponds to 1 MOhm.
    sensitivity: float = 1e6


def random(body: EPuck, cortex: Cortex, sensitivity: float) -> Pyramid:
    """Instantiate a random pyramid to connect the robot body to the brain."""

    motors = sample(range(cortex.component.ws_count), len(body.motors))
    motors = map(lambda v: v + cortex.component.ws_skip, motors)
    return Pyramid(dict(zip(body.motors, motors)), sensitivity)


def evolve_sensitivity(parent: Pyramid) -> Pyramid:
    """Evolve the sensitivity of the motors/actuators (i.e., their load)."""

    return Pyramid(parent.mapping, max(0.0, parent.sensitivity * gauss(1, 0.2)))


def describe(instance: Pyramid) -> str:
    """Return a custom string representation of the object."""

    return 'Motor load: {:.0e}'.format(instance.sensitivity)
