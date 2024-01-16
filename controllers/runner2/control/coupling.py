from control.interface import Interface
from control.network import Network
from dataclasses import dataclass
from inout.loader import configs
from random import sample, gauss
from typing import Dict, Tuple
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

    mapping: Dict[str, Tuple[int, float]] = dict(zip(
        (get_actuators(robot) | get_sensors(robot)).keys(),
        zip(
            sample(
                range(network.cc.ws_skip, network.cc.ws_skip + network.cc.ws_count),
                sensors_count + actuators_count
            ),
            map(lambda _: max(0.0, gauss(MU, SIGMA)), range(sensors_count + actuators_count))
        )
    ))
    for key in get_actuators(robot).keys():
        mapping[key] = mapping[key][0], MOTOR_LOAD

    return Coupling(Interface(mapping.items()))


__all_ = "Coupling", "random_coupling"
