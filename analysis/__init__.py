import random

from logger import logger
from robot.component import IRSensor
from robot.component.motor import Motor
from functools import reduce
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import stimulate
from robot.cortex import new as new_cortex, Cortex
from robot.thalamus import random as random_thalamus, Thalamus
from typing import Iterable, Dict, Tuple
from utils import adapt

default_datasheet: Datasheet = Datasheet(
    wires_count=100,
    Lx=30, Ly=30,
    mean_length=10, std_length=10 * 0.35
)
sensor_range = IRSensor.range(IRSensor())
motors_range = Motor.range(reverse=False)


def collapse_history(data: Iterable):
    """
    Take an history in the form [state, state, state, ...], where 'state' is in
    the form {var_1: value, var_2: value, ...} and collapse it to a the form
    {var_1: [value, value, ...], var_2: [value, value, ...]}
    """
    return reduce(lambda a, b: {k: a.get(k, []) + [b[k]] for k in b}, data, {})


class Placeholder:
    pass


def generate(
        data: Datasheet = default_datasheet,
        load: float = 0,
        seed: int = None
) -> Tuple[Cortex, Thalamus]:
    """
    Generate a device, a conductor and a set of connections to instantiate and
    perform experiments in a shorter and cleaner way.
    """
    if seed:
        random.seed(seed)

    cortex = new_cortex(data)

    placeholder = Placeholder()
    placeholder.sensors = ['s']
    placeholder.motors = ['m']

    thalamus = random_thalamus(cortex, placeholder, load)

    return cortex, thalamus


def copy(
        cortex: Cortex,
        thalamus: Thalamus,
        load: float = None
) -> Tuple[Cortex, Thalamus]:
    """
    Generate a device, a conductor and a set of connections to instantiate and
    perform experiments in a shorter and cleaner way.
    """

    cortex = Cortex(cortex.network.copy(), cortex.datasheet)

    placeholder = Placeholder()
    placeholder.sensors = ['s']
    placeholder.motors = ['m']

    load = load if load else thalamus.sensitivity
    thalamus = Thalamus(thalamus.sensors, thalamus.motors, load)

    return cortex, thalamus


def evaluate(
        cortex: Cortex,
        thalamus: Thalamus,
        stimulus: Dict[str, float],
        time: float,
        i_range: Tuple[float, float] = sensor_range,
        o_range: Tuple[float, float] = motors_range
):
    graph, working_range = cortex.network, cortex.working_range

    read = {thalamus.sensors[s]: v for s, v in stimulus.items()}
    read = [(k, adapt(v, i_range, working_range)) for k, v in read.items()]
    load = [(pin, thalamus.sensitivity) for pin in thalamus.motors.values()]

    stimulate(graph, cortex.datasheet, time, read, load, set())

    outs = [(m, graph.nodes[p]['V']) for m, p in thalamus.motors.items()]
    return {k: adapt(v, working_range, o_range) for k, v in outs}


logger.propagate = False
