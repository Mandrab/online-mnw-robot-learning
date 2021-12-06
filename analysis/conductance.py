import matplotlib.pyplot as plt

from utils import *


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
single_ax, zoom_ax = None, None

delay_range = [1, 2.5, 3, 10]
colors = ['b', 'tab:orange', 'g', 'r']
iterations = range(250)

for delay, color in zip(delay_range, colors):
    c.network = graph.copy()
    conductances = []
    for _ in iterations:
        c.evaluate(delay, {'s': sensor_range[1]}, sensor_range, motors_range, 1)
        conductances += [
            sum(
                [c.network[n1][n2]['Y'] for n1, n2 in c.network.edges()]
            ) / c.network.number_of_edges()
        ]
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

    print('Period length (-1 = no period): ', period_length(
        conductances[50:],
        min_length=10,
        max_length=1000,
        tolerance=max(conductances[50:]) * 0.01  # can differ 1% of max value
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
# CONDUCTANCE ANALYSIS IN DENSITY CHANGES

fig, ax = plt.subplots()

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

for density, (wires, size, length) in densities.items():
    print(density, wires * length * length / (size * size))
    graph, c, _1, _2 = generate(Datasheet(
        wires_count=wires,
        Lx=size, Ly=size,
        mean_length=length, std_length=length * 0.35
    ))
    conductances = []
    for _ in iterations:
        c.evaluate(delay, {'s': sensor_range[1]}, sensor_range, motors_range, 1)
        conductances += [
            sum(
                [c.network[n1][n2]['Y'] for n1, n2 in c.network.edges()]
            ) / c.network.number_of_edges()
        ]
    ax.plot(conductances, label=f'Density {density}')

ax.set_xlabel('iterations')
ax.set_ylabel('average conductivity')
ax.legend(loc='upper right')

plt.title(
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

plt.figure()

delay_range = [_ / 100.0 for _ in range(1, 1750, 1)]
iterations = 250
stability_discard = 200

for delay in delay_range:
    c.network = graph.copy()
    conductances = []
    for _ in range(iterations):
        c.evaluate(delay, {'s': sensor_range[1]}, sensor_range, motors_range, 1)
        conductances += [
            sum(
                [c.network[n1][n2]['Y'] < 0.01 for n1, n2 in c.network.edges()]
            ) / c.network.number_of_edges()
        ]
    conductances = conductances[stability_discard:]
    plt.plot(
        [delay] * (iterations - stability_discard),
        conductances,
        'ko',
        markersize=1
    )

plt.ylabel('average conductivity')
plt.xlabel('relaxation time/frequency [s/Hz]')
labels = [
    (i, f'{d}/{round(1.0/d, 2)}')
    for i, d in enumerate(delay_range) if not i % 350
]
positions = [p for p, _ in labels]
labels = [l for _, l in labels]
plt.xticks(positions, labels)
plt.show()
