import random

from robot.component import IRSensor
from robot.component.Motor import Motor
from robot.conductor import Conductor
from functools import reduce
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import minimum_viable_network, random_nodes
from nanowire_network_simulator import minimum_distance_selection
from typing import Iterable

random.seed(1234)


def collapse_history(data: Iterable):
    """
    Take an history in the form [state, state, state, ...], where 'state' is in
    the form {var_1: value, var_2: value, ...} and collapse it to a the form
    {var_1: [value, value, ...], var_2: [value, value, ...]}
    """
    return reduce(lambda a, b: {k: a.get(k, []) + [b[k]] for k in b}, data, {})


def generate(data: Datasheet):
    """
    Generate a device, a conductor and a set of connections to instantiate and
    perform experiments in a shorter and cleaner way.
    """

    network, _ = minimum_viable_network(data)

    conductor = Conductor(network, data)

    motors = random_nodes(network, set())
    conductor.actuators = dict(zip(['m'], motors))

    neighbor = minimum_distance_selection(motors, 2, True)(network, list(), -1)
    inputs = [*random_nodes(network, neighbor)]
    conductor.sensors = dict(zip(['s'], inputs))

    conductor.initialize()

    return network, conductor, motors, inputs


datasheet = Datasheet(
    wires_count=100,
    Lx=30, Ly=30,
    mean_length=10, std_length=10 * 0.35
)
graph, c, actuators, sensors = generate(datasheet)

sensor_range = IRSensor.range(IRSensor())
motors_range = Motor.range(reverse=False)
