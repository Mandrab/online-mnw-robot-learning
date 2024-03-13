from control.interface import Interface
from control.network import Network
from dataclasses import dataclass
from inout.loader import configs
from random import sample, gauss
from webots.robot import get_actuators, get_sensors, robot

MU: float = configs["sensors"]["multipliers"]["creation_mu"]
SIGMA: float = configs["sensors"]["multipliers"]["creation_sigma"]
MOTOR_LOAD: float = configs["actuators"]["loads"]


@dataclass
class Coupling:
    interface: Interface    # the interface representing the control configuration
    performance: float = 0  # if evaluated, the performance of the control configuration


def random_coupling(network: Network) -> Coupling:
    # calculate the number of inputs and outputs
    sensors_count = len(get_sensors(robot))
    actuators_count = len(get_actuators(robot))

    # select the nodes to which connect the sensors/actuators
    nodes = sample(range(network.cc.ws_skip, network.cc.ws_skip + network.cc.ws_count), sensors_count + actuators_count)

    mapping = dict(zip(
        get_actuators(robot).keys(),
        zip(
            nodes[:actuators_count],            # the index of the node to which the actuator connects to
            [MOTOR_LOAD] * actuators_count,     # the load of the actuator
            range(actuators_count)              # the index of the actuator in the c-interface
        )
    ))

    # generate the initial signals multipliers
    multipliers = map(lambda _: max(0.0, gauss(MU, SIGMA)), range(sensors_count))

    mapping |= dict(zip(
        get_sensors(robot).keys(),
        zip(
            nodes[actuators_count:],            # the index of the node to which the sensor connects to
            multipliers,                        # the multiplier of the sensor signal
            range(sensors_count)                # the index of the sensor in the c-interface
        )
    ))

    return Coupling(Interface(mapping.items()))


__all_ = "Coupling", "random_coupling"
