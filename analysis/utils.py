import random

from conductor import Conductor
from epuck import EPuck
from functools import reduce
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import minimum_viable_network, random_nodes, \
    minimum_distance_selection
from typing import Iterable

random.seed(1234)


def collapse_history(states: Iterable):
    """
    Take an history in the form [state, state, state, ...], where 'state' is in
    the form {var_1: value, var_2: value, ...} and collapse it to a the form
    {var_1: [value, value, ...], var_2: [value, value, ...]}
    """
    return reduce(
        lambda a, b: {k: a.get(k, []) + [v] for k, v in b.items()},
        states, dict()
    )


def generate(datasheet: Datasheet):
    """
    Generate a device, a conductor and a set of connections to instantiate and
    perform experiments in a shorter and cleaner way.
    """

    graph, _ = minimum_viable_network(datasheet)

    conductor = Conductor(graph, datasheet)

    actuators = random_nodes(graph, set())
    conductor.actuators = dict(zip(['m'], actuators))

    neighbor = minimum_distance_selection(
        outputs=actuators,
        distance=2,
        negate=True
    )(graph, list(), -1)
    sensors = [*random_nodes(graph, neighbor)]
    conductor.sensors = dict(zip(['s'], sensors))

    conductor.initialize()

    return graph, conductor, actuators, sensors


datasheet = Datasheet(
    wires_count=100,
    Lx=30, Ly=30,
    mean_length=10, std_length=10 * 0.35
)
graph, c, actuators, sensors = generate(datasheet)

sensor_range = next(iter(EPuck.sensors)).range()
motors_range = next(iter(EPuck.motors)).range(reverse=False)
