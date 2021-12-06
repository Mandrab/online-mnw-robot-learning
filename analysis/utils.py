import random

from conductor import Conductor
from epuck import EPuck
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import minimum_viable_network, random_nodes, \
    minimum_distance_selection

random.seed(1234)


def generate(datasheet: Datasheet):
    graph, _ = minimum_viable_network(datasheet)

    c = Conductor(graph, datasheet)

    actuators = random_nodes(graph, set())
    c.actuators = dict(zip(['m'], actuators))

    neighbor = minimum_distance_selection(
        outputs=actuators,
        distance=2,
        negate=True
    )(graph, list(), -1)
    sensors = [*random_nodes(graph, neighbor)]
    c.sensors = dict(zip(['s'], sensors))

    c.initialize()

    return graph, c, actuators, sensors


datasheet = Datasheet(
    wires_count=100,
    Lx=30, Ly=30,
    mean_length=10, std_length=10 * 0.35
)
graph, c, actuators, sensors = generate(datasheet)

sensor_range = next(iter(EPuck.sensors)).range()
motors_range = next(iter(EPuck.motors)).range(reverse=False)
