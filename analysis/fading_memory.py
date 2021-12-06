"""
This analysis evaluate if the network ends up in different states according to
its recent history.
"""
import math
import matplotlib.pyplot as plt

from functools import reduce
from nanowire_network_simulator import plot, Evolution
from utils import *


################################################################################
# EVALUATION OF MEMORY FADING PROPERTY
# The following graphs shows the property of the network to change its behaviour
# when subject to different histories. Specifically, when the network has
# already been stimulated, it maintains memory of the stimulation for a short
# period of time, in the order of the seconds. This change its future response
# to stimuli.
# As visible by the graph, the first stimulation lower the overall network
# resistance, making the graph less sensible to future stimulation. This is due
# to the fact that part of the voltage does not fall anymore in the network, but
# is instead moved on the sides of the motor/load. Consequently, as more time
# elapse between the two stimulation, the more the network will relax and the
# more it will be subject to the new signals. This is visible by comparing the
# first signal history and the second. In the first, the network does not have
# time to relax, resulting in a lower final stimulation. In the second, the
# network is freshly stimulated and thus it responds fastly to it. Logically,
# after long periods of time the influence of the first stimulation fades,
# making the network ready again for new stimulation. This is a perfect
# representation of the so called 'fading memory' property.
# Finally, it is interesting to note that, although the average conductance
# decrease for near signals, the maximum one increase. This is due to a longer
# time of stimulation of the best/shortest path: it has already been said indeed
# that the stimulation is more effective on short paths. The hypothesis is then
# that the lower-voltage stimulation is balanced by the higher intensity/
# influence on those paths. todo check again
# This behaviour can be seen as a sort of adaptation to stimulated states. To
# force a parallelism to a natural behaviour, it resemble the process by which
# a person or animal get used to harsh life conditions, responding weakly to
# stimulus that it started to get used to.

def network_states(signal):
    # stimulate the first graph with the signal
    c.network = graph.copy()
    for value in signal:
        c.evaluate(1, {'s': value}, (0, 1), (0, 1), 100)

    conductance = [c.network[a][b]['Y'] for a, b in c.network.edges()]
    return sum(conductance) / len(conductance), max(conductance)


def __influence(iteration_distances):
    fig = plt.figure(figsize=(12, 10))
    main, other = fig.subfigures(2, 1, height_ratios=[2, 3])

    def signals(spacing):
        # represent on input signal at one moment in the time
        sin = [math.sin(_ / 10.0) for _ in range(0, 30, 4)]

        # add padding
        signal_1 = [.0] * 75 + sin + [.0] * spacing

        # add final encounter
        signal_1 += sin[:int(len(sin) * .75)]

        # create a second signal
        signal_2 = sin[:int(len(sin) * .75)]

        # make them of the same length
        signal_2 = [.0] * (len(signal_1) - len(signal_2)) + signal_2

        return signal_1, signal_2

    # calculate min, max and avg conductance in the network
    statistics_1 = []
    statistics_2 = []

    for distance in iteration_distances:
        s1, s2 = signals(distance)
        statistics_1 += [network_states(s1)]
        statistics_2 += [network_states(s2)]

    def collapse(a, b): return tuple([e[0] + [e[1]] for e in zip(a, b)])
    statistics_1 = reduce(collapse, statistics_1, ([], [], []))
    statistics_2 = reduce(collapse, statistics_2, ([], [], []))

    for ax, r1, r2, label in zip(
            main.subplots(1, 2), statistics_1, statistics_2,
            ('Average conductance', 'Maximum conductance')
    ):
        ax.plot(iteration_distances, r1, color='b', label='signal 1')
        ax.plot(iteration_distances, r2, color='r', label='signal 2')
        ax.legend(loc='center right')
        ax.set_yscale('log')
        ax.set(title=label, xlabel='Time distance [s]', ylabel='Conductance')

    plot_distance = iteration_distances[3]
    for signal, (left_ax, right_ax) in zip(
            signals(plot_distance), iter(other.subplots(2, 2))
    ):
        # plot signal
        left_ax.plot([_ * 10 for _ in signal], label='voltage')
        left_ax.tick_params(axis='y', labelcolor='tab:blue')
        left_ax.set(
            title=f'Input signal',
            xlabel='Iterations', ylabel='Voltage'
        )
        left_ax.set_xlim([70, len(signal)])

        # create second scale
        left_ax = left_ax.twinx()

        # save average conductance
        mean_conductance = []

        # stimulate the first graph with the signal
        c.network = graph.copy()
        for value in signal:
            c.evaluate(1, {'s': value}, (0, 1), (0, 1), 100)
            conductance = [c.network[a][b]['Y'] for a, b in c.network.edges()]
            mean_conductance += [sum(conductance) / len(conductance)]

        left_ax.plot(mean_conductance, color='tab:red', label='conductance')
        left_ax.tick_params(axis='y', labelcolor='tab:red')
        left_ax.set(ylabel='Conductance')

        plot.conductance_map(fig, right_ax, Evolution(
            datasheet,
            wires_dict={}, delta_time=0.1, grounds=set(),
            loads={(a, 1) for a in actuators},
            network_instances=[
                (c.network, [(s, 1) for s in sensors])
            ]))

    plt.suptitle('Network conductance according to different input sequences')
    plt.subplots_adjust(wspace=.35, hspace=.45)
    plt.show()


# time to relax: 150s
__influence([*range(0, 25, 1)])

# exit() todo real sensors data test
#
# AVOID_FILE = 'avoid_obstacle_sensors_readings.dat'
# DIRECT_FILE = 'direct_moving_sensors_readings.dat'
#
# # save sensors readings to file
# with open(DIRECT_FILE, 'r') as file:
#     readings_a = json.loads(file.read())
#
# # save sensors readings to file
# with open(AVOID_FILE, 'r') as file:
#     readings_b = json.loads(file.read())
#
# # take readings until start of obstacle perception
# first = [*takewhile(lambda d: all([v < 80 for v in d.values()]), readings_b)]
#
# # remove taken values from lists
# readings_b = readings_b[len(first):]
#
# # take values until 'end' of obstacle perception
# second = [*takewhile(lambda d: any([v > 80 for v in d.values()]), readings_b)]
#
# # takes readings of last obstacle and attach to previously processed readings
# # (to make both end with same readings)
# third = [*takewhile(
#     lambda d: any([v > 80 for v in d.values()]), reversed(readings_a)
# )]
#
# # reduce data to better format
# imix = iter(first + second + first + third)
# keys = {k: [v] for k, v in next(imix).items()}
# for d in imix:
#     for k, v in d.items():
#         keys[k].append(v)
#
# fig, ax = plt.subplots()
# for k in keys:
#     ax.plot(keys[k])
# plt.show()
#
# # get lists lengths
# difference = len(readings_a) - len(readings_b)
#
# # if a is longer than b, discard older values
# if difference > 0:
#     readings_a = readings_a[difference:]
#
# # if b is longer than a, discard older values
# if difference < 0:
#     readings_b = readings_b[-difference:]
#
# print('a', readings_a, '\nb', readings_b)
