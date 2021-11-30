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

def __generate(datasheet: Datasheet):
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

    return graph, c, actuators, sensors


datasheet = Datasheet(
    wires_count=100,
    Lx=30, Ly=30,
    mean_length=10, std_length=10 * 0.35
)
graph, c, actuators, sensors = __generate(datasheet)


################################################################################
# RESPONSE ANALYSIS IN FREQUENCY CHANGES
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
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(7, 16))
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

        values_ax.plot(x, y, label=f'frequency {1.0 / value} Hz')

        e = Evolution(
            datasheet,
            wires_dict={}, delta_time=value, grounds=set(),
            loads={(a, 1) for a in actuators},
            network_instances=[
                (c.network, [(s, sensor_range[1]) for s in sensors])
            ])

        plot.conductance_map(fig, ax, e)
        ax.set_title(f'Conductance in {1 / value} Hz updated network')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.subplots_adjust(top=0.95, bottom=0.03, hspace=0.4)

    plt.suptitle(
        'Analysis of the update frequency influence in the signal propagation'
    )
    plt.show()


__influence([0.1, 5, 10])


################################################################################
# RESPONSE ANALYSIS IN LOAD CHANGES
# The following graphs show the influence of the motor resistance in the
# stimulation of the network.
# When the resistance is low, just a small amount of tension 'fall' at the sides
# of the motor. This cause the network to be highly stimulated, in that the vast
# majority of the tension falls inside the device.
# todo Sure? Check paper. Make graph of voltage fall (V_source - V_output)
# Differently, when the device is connected to an 'heavy' load, an high voltage
# is measurable at the sides of the motor. This makes the network just softly
# stimulated, and prevents any interesting plasticity to show-up.
# It is also interesting to note that an high load directly influences the motor
# speed. Indeed, an higher voltage will insists on the motor, making it move
# fastly.
# The said properties are opposite: high plasticity brings to low speed; low
# plasticity to high speed. Given a complex system that need both, a solution
# may consists in the adjustment of the output value to a specific range.
# This may be achieved through the connection of a transistor and a carefully
# chosen resistance as to allow the control with higher voltages. This would
# however complicate the hardware solution. A more evolutionary oriented ways is
# to find a balance of the two properties.

def __influence(values):
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(7, 16))
    values_ax, *axs = axs

    for ax, value in zip(axs, values):
        # avoid modify the graph
        c.network = graph.copy()

        step = lambda i: c.evaluate(
            update_time=0.1,  # seconds
            inputs={'s': i},
            inputs_range=sensor_range,
            outputs_range=motors_range,
            actuators_load=value
        )

        io = {
            i: [v for v in step(i).values()][0]
            for i in range(*sensor_range, 128)
        }

        # make data
        x = [*io.keys()]
        y = [*io.values()]

        values_ax.plot(x, y, label=f'resistance {value} Ohm')

        e = Evolution(
            datasheet,
            wires_dict={}, delta_time=value, grounds=set(),
            loads={(a, value) for a in actuators},
            network_instances=[
                (c.network, [(s, sensor_range[1]) for s in sensors])
            ])

        plot.conductance_map(fig, ax, e)
        ax.set_title(f'Conductance in network with {value} Ohm load')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.subplots_adjust(top=0.95, bottom=0.03, hspace=0.4)

    plt.suptitle(
        'Analysis of the motor resistance influence in the signal propagation'
    )
    plt.show()


__influence([1, 100, 10000])


################################################################################
# RESPONSE ANALYSIS IN DENSITY CHANGES
# The following charts show the changes in the network behaviour at the increase
# of the nano-wires density.
# todo down, also the signal propagation?
# With an high density, the signal propagation and the emergence of well defined
# paths is smaller. This is due to the fact that the density means an increase
# in the number of nano-wires (a.k.a. resistances) in the device. This is
# comparable with an electronic circuit with parallel resistors: the more, the
# lower the overall resistance become. This characteristic collides with the
# fixed load's resistance, moving a percentage of the voltage fall at the sides
# of the motor.
# As for the load's resistance, this property implies that an increment in the
# network density will cause an increase in the output value and a consequently
# decrease in the network plasticity. The choose of a correct density should
# then seek for a balance between the output values and the network plasticity.

def __influence(values):
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(7, 16))
    values_ax, *axs = axs

    for ax, value in zip(axs, values):
        graph, c, actuators, sensors = __generate(value)

        step = lambda i: c.evaluate(
            update_time=0.1,  # seconds
            inputs={'s': i},
            inputs_range=sensor_range,
            outputs_range=motors_range,
            actuators_load=50
        )

        io = {
            i: [v for v in step(i).values()][0]
            for i in range(*sensor_range, 128)
        }

        # make data
        x = [*io.keys()]
        y = [*io.values()]

        values_ax.plot(x, y, label=f'wires {value.wires_count}')

        e = Evolution(
            datasheet,
            wires_dict={}, delta_time=value, grounds=set(),
            loads={(a, value) for a in actuators},
            network_instances=[
                (c.network, [(s, sensor_range[1]) for s in sensors])
            ])

        plot.conductance_map(fig, ax, e)
        ax.set_title(f'Conductance in network with {value.wires_count} wires')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.subplots_adjust(top=0.95, bottom=0.03, hspace=0.4)

    plt.suptitle(
        'Analysis of the wires density influence in the signal propagation'
    )
    plt.show()


__influence([
    Datasheet(
        wires_count=100,
        Lx=30, Ly=30,
        mean_length=10, std_length=10 * 0.35
    ), Datasheet(
        wires_count=300,
        Lx=30, Ly=30,
        mean_length=10, std_length=10 * 0.35
    ), Datasheet(
        wires_count=500,
        Lx=30, Ly=30,
        mean_length=10, std_length=10 * 0.35
    )
])


################################################################################
# CONDUCTANCE ANALYSIS IN FREQUENCY CHANGES
# This graphs shows how the conductance vary for relatively low refresh rates.
# For higher frequencies, the conductance converge to a fixed point. This is
# already visible from f = 1, where the conductance converge to a fixed point.
# This is due to the fact that higher frequencies does not give time to the
# network to relax.
# Very low frequencies converge instead to a multi-points attractor. We can see,
# for example, that with 0.1 Hz the conductance oscillate between two points.
# Finally, for a certain range of values we can see that the conductance
# oscillate in a chaotic way. This happens, for example, for the 0.4 Hz
# frequency. An analysis of the 'conductance-signal' shows indeed that no
# repetition appears in it, at least in the short period.

def period_length(
        samples,
        min_length: int,
        max_length: int,
        tolerance: float = 0.0
):
    """
    Parameters:
    -----------
    samples:
        the signal's values
    max_distance:
        max distance between the start of two periods. In other words, the max
        accepted period length
    min_length:
        min length of the signal to be considered repeated (e.g. has [1,2,3,1]
        to be considered repeated?)
    tolerance:
        accepted distance between the two values (e.g. if 1.5 and 1.4 should be
        or not considered the same)

    Examples:
    ---------
    period_length([1,2,3,1], 1, 2, 1) -> -1 (max distance is 2)
    period_length([1,2,3,1], 1, 3, 1) -> 3
    period_length([1,2,3,1,2,3], 1, 3, 1) -> 3
    period_length([1,2,3,1,2,3,4], 1, 3, 1) -> -1 (4 breaks the period)
    period_length([1,2,3,1,2,3,1,2,3], 1, 3, 1) -> 3
    period_length([1,2,3,1,2,3,1,2,3,4], 1, 3, 1) -> -1 (4 breaks the period)
    period_length([1,2,3,1,2], 2, 3, 1)) -> 3
    period_length([1,2,3,1,2], 3, 3, 1)) -> -1 ([1,2] is too short to be
        considered a repetition/period)
    """
    for distance in range(1, max_length +1):
        if len(samples) - distance < min_length:
            return -1
        diffs = [a-b for a, b in zip(samples, samples[distance:])]
        if len(diffs) > 0 and all(abs(d) <= tolerance for d in diffs):
            return distance
    return -1


fig = plt.figure(figsize=(8, 4))
main, other = fig.subfigures(1, 2)
ax = main.subplots(1, 1)
axs = iter(other.subplots(4, 2))

delay_range = [1, 2.5, 3, 10]
colors = ['b', 'tab:orange', 'g', 'r']
iterations = range(250)

for delay, color in zip(delay_range, colors):
    c.network = graph.copy()
    voltages = []
    for _ in iterations:
        c.evaluate(delay, {'s': sensor_range[1]}, sensor_range, motors_range, 1)
        voltages += [
            sum(
                [c.network[n1][n2]['Y'] for n1, n2 in c.network.edges()]
            ) / c.network.number_of_edges()
        ]
    ax.plot(voltages[:50], color=color, label=f'{round(1 / delay, 2)}Hz')
    single_ax, zoom_ax = next(axs)
    single_ax.plot(voltages[:30], color=color)
    zoom_ax.plot([i + 220 for i in range(30)], voltages[-30:], color=color)
    single_ax.set_xticks([])
    single_ax.set_yticks([])
    zoom_ax.set_xticks([])
    zoom_ax.yaxis.tick_right()
    position = zoom_ax.get_position()
    position.x0 = 0.5
    zoom_ax.set_position(position)

    print('Period length (-1 = no period): ', period_length(
        voltages[50:],
        min_length=10,
        max_length=1000,
        tolerance=max(voltages[50:]) * 0.01  # can differ 1% of max value
    ))

position = ax.get_position()
position.x0 = 0.2
position.x1 = 1
ax.set_position(position)
ax.set_xlabel('iterations')
ax.set_ylabel('average conductivity')

single_ax.set_xticks([0, 30, 15])
zoom_ax.set_xticks([220, 235, 250])

handles, labels = ax.get_legend_handles_labels()
plt.legend(
    handles,labels,
    ncol=4, loc='lower right', bbox_to_anchor=(1.05, -0.8)
)
plt.title(
    'Average conductance after continuous stimulation at different frequencies',
    y=4.8, x=-1.1
)
plt.show()


################################################################################
# CONDUCTANCE ANALYSIS IN FREQUENCY CHANGES
# The previously described property is shown also in the following graph.
# This plot, for different frequencies, the values of the attractor.
# This exclude the 'stability-reaching' period, discarding the first iterations'
# results.

plt.figure()

delay_range = [_ / 10.0 for _ in range(1, 175, 1)]
iterations = 250
stability_discard = 200

for delay in delay_range:
    c.network = graph.copy()
    voltages = []
    for _ in range(iterations):
        c.evaluate(delay, {'s': sensor_range[1]}, sensor_range, motors_range, 1)
        voltages += [
            sum(
                [c.network[n1][n2]['Y'] < 0.01 for n1, n2 in c.network.edges()]
            ) / c.network.number_of_edges()
        ]
    voltages = voltages[stability_discard:]
    plt.plot(
        [delay] * (iterations - stability_discard),
        voltages,
        'ko',
        markersize=1
    )

plt.xlabel('relaxation time')
plt.ylabel('average conductivity')
plt.show()
