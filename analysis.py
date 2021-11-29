import matplotlib.pyplot as plt
import random

from conductor import Conductor
from epuck import EPuck
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import minimum_viable_network, random_nodes, \
    minimum_distance_selection, plot, Evolution

random.seed(1234)
sensor_range = next(iter(EPuck.sensors)).range()
motors_range = next(iter(EPuck.motors)).range(reverse=False)

################################################################################
# SETUP

datasheet = Datasheet(
    wires_count=100,
    Lx=30, Ly=30,
    mean_length=10, std_length=10 * 0.35
)
graph, _ = minimum_viable_network(datasheet)

c = Conductor(graph, datasheet)

actuators = [*random_nodes(graph, set())]
c.actuators = dict(zip(['m'], actuators))

neighbor = minimum_distance_selection(
    outputs=actuators,
    distance=2,
    take_neighbor=True
)(graph, list(), -1)
sensors = [*random_nodes(graph, neighbor)]
c.sensors = dict(zip(['s'], sensors))

c.initialize()

################################################################################
# RESPONSE ANALYSIS
# The following graphs shows the variance of the motor output, in a random
# connection, according to the sensor input at different frequencies.
# When the frequency is high, the best path is continuously/highly stimulated
# and increase its conductivity. When the frequency is low the path relax after
# each stimulation and only the neighbor arches become conductive.
# This behaviour make the output higher in the first case, in that the voltage
# 'fall' more in the motor-ground arch than in the rest of the network.
# This suggests that high frequently updated network are more likely to change
# their behaviour runtime, possibly increasing capabilities.

def __influence(values):
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(8, 20))
    values_ax, *axs = axs

    for ax, value in zip(axs, values):
        # avoid modify the graph
        c.network = graph.copy()

        step = lambda i: c.evaluate(
            update_time=value,  # seconds
            inputs={'s': i},
            inputs_range=sensor_range,
            outputs_range=motors_range,
            actuators_load=100
        )

        io = {
            i: [v for v in step(i).values()][0]
            for i in range(*sensor_range, 128)
        }

        # make data
        x = [*io.keys()]
        y = [*io.values()]

        values_ax.plot(x, y, label=f'frequency {1.0 / value}Hz')

        e = Evolution(
            datasheet,
            wires_dict={}, delta_time=value, grounds=set(),
            loads={(a, 1) for a in actuators},
            network_instances=[
                (c.network, [(s, sensor_range[1]) for s in sensors])
            ])

        plot.conductance_map(fig, ax, e)
        ax.set_title(f'Conductance in {1 / value}Hz updated network')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.show()

__influence([0.1, 5, 10])
