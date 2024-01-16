from control.coupling import Coupling, random_coupling
from control.network import Network, random_network
from control.tsetlin.tsetlin import Tsetlin
from ctypes import c_double
from dataclasses import dataclass
from functools import reduce
from inout.loader import configs
from math import copysign
from nnspy import nns
from operator import __sub__
from simulation.history import History
from typing import Tuple
from webots.robot import get_actuators, get_sensors, robot

TIME_STEP = configs["time_step_ms"]
MAX_INPUT = configs["max_input"]
MAX_OUTPUT = configs["max_output"]
MAX_V = configs["nn network"]["max_stimulation_v"]


@dataclass
class Replica:

    network: Network                # the nanowire-network controller of the robot
    configuration: Coupling         # the actual control configuration
    history: History                # the history of tried configurations and the holder of the best controller known
    tsetlin: Tsetlin                # the adaptation logic of the configuration


def random_replica(seed: int):
    nw_network = random_network(seed)
    control_configuration = random_coupling(nw_network)
    history = History(Coupling(control_configuration.interface.copy()))
    return Replica(nw_network, control_configuration, history, Tsetlin())


def run(replica: Replica):
    interface = replica.configuration.interface

    # if the webots simulation is paused or stopped, return
    if robot.step(TIME_STEP) == -1:
        return

    # get normalized sensors readings (range [0, 1]) and apply multiplier
    reads = [(n, range2range(s.getValue(), (0, MAX_INPUT))) for n, s in get_sensors(robot).items()]
    reads = [(n, v * interface.multipliers.get(n, 1.0)) for n, v in reads]

    # put the input signal in the range supported by the network
    reads = [(n, range2range(v, out_range=(0, MAX_V))) for n, v in reads]

    # create the stimulation array to pass to the stimulate function
    ios = (c_double * interface.c_interface.sources_count)()

    # set the voltages of the ios array according to the readings
    for i, (_, value) in enumerate(reads):
        ios[i] = value

    # stimulate the network with the sensors inputs
    nns.update_conductance(replica.network.ns, replica.network.cc)
    nns.voltage_stimulation(replica.network.ns, replica.network.cc, interface.c_interface, ios)

    # extract outputs from network and remap output values to motor speeds
    outs = {a: interface.pins[n] for n, a in get_actuators(robot).items()}
    outs = {a: replica.network.ns.Vs[i] for a, i in outs.items()}

    # set the motors' speed according to the network output
    for motor, value in outs.items():
        motor.setPosition(float('inf'))
        motor.setVelocity(range2range(value, (0, MAX_V), (MAX_OUTPUT, -MAX_OUTPUT)))


def range2range(value: float, in_range: Tuple[float, float] = (0, 1), out_range: Tuple[float, float] = (0, 1)) -> float:
    in_delta: float = reduce(__sub__, reversed(in_range))
    out_delta: float = reduce(__sub__, reversed(out_range))
    value = (value - min(in_range)) * out_delta / in_delta
    value = out_range[0] + copysign(value, out_delta)

    # force bounds to the value and return it
    return max(min(value, max(out_range)), min(out_range))
