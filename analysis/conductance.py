import matplotlib.pyplot as plt

from analysis import *
from networkx import Graph


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
# Note: if we stimulate every 0.1s, alternating high and low inputs and
# increasing the time between the high ones (e.g. high, low, ..., low, high,
# etc.), the values for which the behaviour is seen are a bit lower. This is
# probably due to imprecision in the simulator. However, the behaviour is the
# same (order, chaos, order), and the difference can thus be ignored.
# Finally, the behaviour of the conductance depends also from the topology of
# the network. This make the system harder to configure and a overall critic
# value hard to find.

def period_length(
        samples: Iterable[float],
        min_length: int,
        max_length: int,
        tolerance: float = .0
):
    """
    Parameters:
    -----------
    samples:
        the signal's values
    min_length:
        min length of the signal to be considered repeated (e.g. has [1,2,3,1]
        to be considered repeated?)
    max_distance:
        max distance between the start of two periods. In other words, the max
        accepted period length
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
    for distance in range(1, max_length + 1):
        if len(list(samples)) - distance < min_length:
            return -1
        diffs = [a-b for a, b in zip(samples, samples[distance:])]
        if len(diffs) > 0 and all(abs(d) <= tolerance for d in diffs):
            return distance
    return -1


fig = plt.figure(figsize=(8, 4))
main, other = fig.subfigures(1, 2)
ax = main.subplots(1, 1)
axs = iter(other.subplots(4, 2))
single_ax, zoom_ax = None, None

delay_range = [1.0, 2.5, 3.0, 10.0]
colors = ['b', 'tab:orange', 'g', 'r']
iterations = range(250)


def average_conductance(cortex: Cortex, thalamus: Thalamus) -> Iterable[float]:
    def step(_: int, g: Graph = cortex.network) -> float:
        evaluate(cortex, thalamus, {'s': max(sensor_range)}, delay)
        return sum(g[n1][n2]['Y'] for n1, n2 in g.edges) / g.number_of_edges()
    return list(map(step, iterations))


for delay, color in zip(delay_range, colors):
    cortex, thalamus = generate(load=1, seed=1234)
    conductances = average_conductance(cortex, thalamus)
    ax.plot(conductances[:50], color=color, label=f'{round(1 / delay, 2)}Hz')
    single_ax, zoom_ax = next(axs)
    single_ax.plot(conductances[:30], color=color)
    zoom_ax.plot([i + 220 for i in range(30)], conductances[-30:], color=color)
    single_ax.set_xticks([])
    single_ax.set_yticks([])
    zoom_ax.set_xticks([])
    zoom_ax.yaxis.tick_right()
    position = zoom_ax.get_position()
    position.x0 = 0.5
    zoom_ax.set_position(position)

    tolerance = max(conductances[50:]) * .01   # can differ 1% of max value
    period = period_length(conductances[50:], 100, 250, tolerance)
    print('Period length: ' + ('not periodic' if period == -1 else str(period)))

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
    handles, labels,
    ncol=4, loc='lower right', bbox_to_anchor=(1.05, -0.8)
)
plt.title(
    'Average conductance after continuous stimulation at different frequencies',
    y=4.8, x=-1.1
)
plt.show()

################################################################################
# CONDUCTANCE ANALYSIS IN DENSITY CHANGES
# The graphs show the behaviour of the conductance in networks generated with
# different densities.
# It is visible that there is an increase in the average conductivity for values
# near to the 'critical value'. This is due to the fact that, with the increase
# in conductivity, the network decrease its resistance and thus less tension
# fall at its sides. This bring to a different response of the networks to the
# same (continuous) inputs.

fig = plt.figure(figsize=(10, 8))
ax, *axs = fig.subplots(2, 1)

densities = {
    4.94: (100, 45, 10),
    5.06: (100, 40, 9),
    5.22: (100, 35, 8),
    5.63: (250, 40, 6),
    5.76: (400, 50, 6),
    6.25: (400, 80, 10)
}
delay = 0.1
iterations = range(50)

max_conductances = []

for density, (wires, size, length) in densities.items():
    cortex, thalamus = generate(Datasheet(
        wires_count=wires,
        Lx=size, Ly=size,
        mean_length=length, std_length=length * 0.35
    ), load=1)
    conductances = average_conductance(cortex, thalamus)
    max_conductances += [max(conductances)]
    ax.plot(conductances, label=f'Density {density}')

ax.set(xlabel='iterations', ylabel='average conductivity')
ax.legend(loc='upper right')

ax = next(iter(axs))
ax.bar(list(map(str, densities.keys())), max_conductances)
ax.set(xlabel='densities', ylabel='max average conductivity')

fig.suptitle(
    'Average conductance after continuous stimulation'
    'in networks with different densities'
)

plt.show()

################################################################################
# CONDUCTANCE ANALYSIS IN FREQUENCY CHANGES
# The previously described property is shown also in the following graph.
# This plot, for different frequencies, the values of the attractor.
# This exclude the 'stability-reaching' period, discarding the first iterations'
# results.

ax = plt.figure().subplots()

delay_range = [_ / 100.0 for _ in range(1, 1750)]
iterations = 250
discard = 200   # discard initial values when the network converge to stability
labels_count = round(len(delay_range) / 7)

for delay in delay_range:
    cortex, thalamus = generate(load=1, seed=1234)

    def step(_: int, g: Graph = cortex.network) -> float:
        evaluate(cortex, thalamus, {'s': sensor_range[1]}, delay)
        return sum(g[a][b]['Y'] < .01 for a, b in g.edges) / g.number_of_edges()
    conductances = list(map(step, range(iterations)))[discard:]
    ax.plot([delay] * (iterations - discard), conductances, 'ko', markersize=1)

ax.set(xlabel='relaxation time/frequency [s/Hz]', ylabel='average conductivity')
labels = [f'{d} s\n{round(1.0/d, 2)} Hz' for d in delay_range]
labels = [(i, l) for i, l in enumerate(labels) if i % labels_count == 0]
positions = [p for p, _ in labels]
labels = [l for _, l in labels]

plt.title(
    'Average conductance after continuous stimulation\n'
    'at different frequencies'
)
plt.xticks(positions, labels)
plt.tight_layout(pad=1.5)
plt.show()
