import json
import matplotlib.pyplot as plt
import scipy.stats as stats

from nanowire_network_simulator import backup
from os import listdir
from os.path import join, isfile
from scipy.signal import savgol_filter
from utils import collapse_history

DIRECTORY = 'controllers/'

################################################################################
# EVALUATION OF THE INFLUENCE OF EACH SENSORS AND THUS BEHAVIOUR OF THE NET IN
# THE BEST CONFIGURATIONS FOUND
# The following plots show the input and output signals (sensor / motor) and the
# resulting direction of the robot. This allows to understand/show that sensors
# perceptions influence directly the direction of the robot, and this is thus
# not only originated by internal mechanism. Moreover, this allows to spot some
# high-level relations between specific sensors' signals and motor outputs.
# The possibly presence of those relations has however to be analysed, in that
# it can imply a non-mediated behaviour of the network. In other words, the
# presence of direct connections (or very influent one) inside the
# network may reduce it to a Braitenberg-like architecture, lacking of
# proper, high-level, mediation/mixing mechanisms.

# import configurations
files = filter(isfile, map(lambda s: join(DIRECTORY, s), listdir(DIRECTORY)))
files = list(filter(lambda _: _.endswith('.dat'), files))
files = sorted(files, key=lambda _: _.split('.')[-2])
chunks = map(lambda i: sorted(files[i * 6:][:6]), range(int(len(files) / 6)))
chunks = list(chunks)
io_signals = [(chunk[4], chunk[3]) for chunk in chunks]
others = [chunk[:3] + chunk[-1:] for chunk in chunks]
others = list(map(lambda _: backup.read(_[1], _[2], _[3], _[0]), others))

# analyse just one device
io_signals = io_signals[1]
graph, datasheet, wires, connections = others[1]
sensors = connections['inputs']
actuators = connections['outputs']


def file_import(name):
    with open(name, 'r') as file:
        result = json.loads(file.read())
    return result


# get sensors readings and motors outputs
i_signals, o_signals = [file_import(file) for file in io_signals]

fig = plt.figure(figsize=(12, 8))
figs = iter(fig.subfigures(3, 1))


def smoother(signal):
    """Approximate signal with a curve; window size 51, polynomial order 3."""
    return savgol_filter(signal, 51, 3)

# plot distances
ax = next(figs).subplots()

for key, signals in collapse_history(i_signals).items():
    signals = [s if s < 5 else 5 for s in signals]
    ax.plot(signals, label=key)

labels = [*map(str, range(5))] + ['[7-5]']
ax.set_yticks(range(len(labels)), labels)
ax.set(title='Sensors readings', xlabel='Iterations', ylabel='Distance')
ax.invert_yaxis()
ax.legend()

# plot direction
ax = next(figs).subplots()

left, right = collapse_history(o_signals).values()
direction = [l - r for l, r in zip(left, right)]
direction = smoother(direction)
ax.plot(direction)
ax.plot([0.0] * len(direction), color='b', linestyle=(0, (5, 5)))
ax.set(title='Robot direction', xlabel='Iterations', ylabel='Direction')
ax.set_yticks(range(-6, 7), ['right', *map(str, range(-10, 11, 2)), 'left'])

# plot motors control signal
axs = iter(next(figs).subplots(1, 2))

for key, command in collapse_history(o_signals).items():
    # approximate signal with a curve; window size 51, polynomial order 3
    command_smooth = smoother(command)
    ax = next(axs)
    ax.plot(command, label='signal')
    ax.plot(command_smooth, color='r', linewidth=3, label='averaged signal')
    ax.set(title=key, xlabel='Iterations', ylabel='Motor output')
    ax.legend()

plt.show()

################################################################################
# EVALUATION OF THE INFLUENCE OF SENSOR 0 IN THE OUTPUT MOTOR COMMAND
# The following graph aims to show that a sensor-motor relation is not obvious
# and may not lead to great changes in the behaviour of the robot.
# The graph shows the variance of the motor output according to the proximity
# value perceived by the sensor 'ps0'. The data come from a simulated robot run,
# and consist in a sequence of the (left command, right command, sensor reading)
# tuple, representing a control instant. Those are then ordered by decreasing
# perceived distance. The values with distance >= 5 are excluded in that
# basically irrelevant in the robot motion. As visible, the left motor behaviour
# seems slightly related to the ps0 input: as the robot go far from the
# obstacle, the value of the motor slightly increase. This seems to not be
# true for the right motor, that behaves instead in a way that does not seems
# to be related to the sensors reading.
# Those observations are however limited in their usage: the first does not
# consider the influence of other sensors with identical/similar signal
# behaviour (that may be indeed the ones that effectively influence the output);
# the second does not consider that the signal behaviour can be the result of
# highly complex signals interactions.

_, ax = plt.subplots()

ps = collapse_history(i_signals)['ps0']
ps = [s if s < 5 else 5 for s in ps]
left = collapse_history(o_signals)['left wheel motor']
right = collapse_history(o_signals)['right wheel motor']

pairs = sorted(zip(ps, left, right))
pairs = [*filter(lambda sd: sd[0] < 5, pairs)]

data = [v for _, v, _ in pairs]
lines = ax.plot(data, color='b', label='left motor')

data = [v for _, _, v in pairs]
lines += ax.plot(data, color='g', label='right motor')
ax.set_ylabel('Motor speed')

ax = ax.twinx()

data = [k for k, *_ in pairs]
lines += ax.plot(data, label='sensor', color='r')
ax.set_ylabel('Distance', color='r')

labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc=0)

plt.show()

################################################################################
# EVALUATION OF THE CORRELATION OF EACH SENSOR IN THE OUTPUT MOTOR COMMANDS
# The following graph show the correlation between the sensor-motor time series.
# The correlation is calculated as the Pearson's correlation coefficient and it
# is almost completely positive due to the characteristic of the system: this
# cause indeed the motor signal to rise when the distance is high (todo check),
# making the correlation almost always positive (some cases may lead to a
# decrease if the higher voltage cause a lower voltage at the side of a wire,
# causing a consequent decrease in the stimulation; todo just hypothesis
# probably wrong).
# If this analysis better shows the signal-motor correlation, it does not
# however guarantee the correlation. As for the previous case indeed, the
# stimulating signal may be another one with similar trend, making the measure
# not valid/biased.

fig, ax = plt.subplots()
# todo delete no signal maybe?
correlations = {
    mk: [
        stats.pearsonr(sv, mv)[0]
        for sk, sv in collapse_history(i_signals).items()
    ]
    for mk, mv in collapse_history(o_signals).items()
}
pcm = ax.pcolormesh(
    correlations.keys(),
    [f'ps{i}' for i in range(8)],
    list(map(list, zip(*correlations.values()))),
    vmin=-1, vmax=1
)
for y, k in enumerate(correlations):
    for x, v in enumerate(correlations[k]):
        print(y, x, k, v)
        plt.text(
            y, x, '%.4f' % v,
            horizontalalignment='center',
            verticalalignment='center',
        )
fig.colorbar(pcm, location='bottom')

plt.show()

#
# # make the conductance decrease in order to analyse its relaxed state (the
# # aim of this analysis is to individuate interesting characteristics of the
# # network and thus the stimulated version shows only a specific response of it).
# inputs = [(i, 0) for i in sensors.values()]
# outputs = {(i, 100) for i in actuators.values()}
# for _ in range(100):
#     stimulate(graph, datasheet, 1e3, [], [], set())
#
# e = Evolution(datasheet, wires, -1, set(), outputs, [(graph, inputs)])
#
# left_resistance, right_resistance = [ [
#         nx.resistance_distance(graph, s, m, weight='Y', invert_weight=False)
#         for s in sensors.values()
#     ] for m in actuators.values()
# ]
# resistances = {'left motor': left_resistance, 'right motor': right_resistance}
#
# fig, ax = plt.subplots(figsize=(9.2, 5))
#
# left_start, right_start = 0, 0
# for i, sensor in enumerate(sensors):
#     ax.bar(
#         resistances.keys(),
#         [left_resistance[i], right_resistance[i]],
#         width=0.35,
#         bottom=[left_start, right_start],
#         label=f'ps{i}'
#     )
#     left_start += left_resistance[i]
#     right_start += right_resistance[i]
#
# ax.set(title='Sensor-Actuator path\'s resistance', ylabel='Resistance')
# ax.legend()
#
# plt.show()
#
# fig, ax = plt.subplots()
# plot.conductance_map(fig, ax, e)
# plt.show()
