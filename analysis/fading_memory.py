"""
This analysis evaluate if the network ends up in different states according to
its recent history.
"""
import math
import matplotlib.pyplot as plt
import networkx as nx

from analysis import *
from nanowire_network_simulator import plot, Evolution
from typing import Any


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

def io_path_conductance(signal: Iterable[float]):
    # stimulate the first graph with the signal
    c, p, t = generate(load=100, seed=1234)

    for value in signal:
        evaluate(c, p, t, {'s': value}, 1, i_range=(0, 1))

    n, i, o = c.network, t.mapping['s'], p.mapping['m']
    return 1 / nx.resistance_distance(n, i, o, weight='Y', invert_weight=False)


def signals(spacing: int) -> Any:
    # represent on input signal at one moment in the time
    sin = [math.sin(_ / 10.0) for _ in range(0, 30, 4)]

    # add padding and final encounter
    signal_1 = [.0] * 75 + sin + [.0] * spacing + sin[:int(len(sin) * .75)]

    # create a second signal and make it of the same length as signal_1
    signal_2 = sin[:int(len(sin) * .75)]
    signal_2 = [.0] * (len(signal_1) - len(signal_2)) + signal_2

    return signal_1, signal_2


def influence(distances):
    def sum_states(a, b): return a + [io_path_conductance(b)]

    c, p, t = generate(load=100, seed=1234)
    ys = []
    for value in (signal := [10.0] * 20 + [0.0] * 30):
        evaluate(c, p, t, {'s': value}, 1, i_range=(0, 10))
        ys += [1 / nx.resistance_distance(
            c.network, t.mapping['s'], p.mapping['m'],
            weight='Y', invert_weight=False
        )]

    _, ax = plt.subplots()
    ax.set_title('I/O path conductance when subject to a signal')
    ax.set(xlabel='Time distance [s]', ylabel='Voltage [V]')
    ax.plot(range(50), signal, color='tab:red')
    ax = ax.twinx()
    ax.plot(range(50), ys, color='tab:blue')
    ax.set_ylabel('Conductance [S]')
    plt.show()

    signal_1s = map(next, map(iter, map(signals, distances)))
    statistics = reduce(sum_states, signal_1s, list())

    _, ax = plt.subplots()
    ax.set_title(
        'I/O path conductance when stimulated\n' +
        'with two signals happening at different time distances'
    )
    ax.set(xlabel='Time distance [s]', ylabel='Conductance [S]')
    ax.plot(distances, statistics)
    plt.show()

    fig = plt.figure(figsize=(12, 6))
    ax = [[plt.subplot(2, 2, i + 2 * r) for i in range(1, 3)] for r in range(2)]
    for s, (lax, rax) in zip(signals(distances[3]), ax):
        lax.plot([_ * 10 for _ in s], label='voltage', color='tab:blue')
        lax.tick_params(axis='y', labelcolor='tab:blue')
        lax.set(title=f'Input signal', xlabel='Time [s]', ylabel='Voltage')
        lax.set_xlim(left=70)

        # create second scale
        lax = lax.twinx()

        # stimulate the first graph with the signal
        c, p, t = generate(load=100, seed=1234)

        def network_avg_conductance(v):
            evaluate(c, p, t, {'s': v}, 1, i_range=(0, 1))
            conductance = [c.network[a][b]['Y'] for a, b in c.network.edges()]
            return sum(conductance) / len(conductance)

        lax.plot(list(map(network_avg_conductance, s)), color='tab:red')
        lax.tick_params(axis='y', labelcolor='tab:red')
        lax.set(ylabel='Conductance [S]')
        lax.set_ylim(top=14e-3)

        plot.conductance_distribution(fig, rax, Evolution(
            default_datasheet, {}, 0.1, set(),
            {(a, 1) for a in nodes(p.mapping)},
            [(c.network, [(s, 1) for s in nodes(t.mapping)])]
        ))

    plt.suptitle('Network conductance according to different input sequences')
    plt.subplots_adjust(wspace=.35, hspace=.45)
    plt.show()


influence(list(range(0, 25)))
