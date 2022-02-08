import json
import matplotlib.pyplot as plt
import networkx as nx
import scipy.stats as stats

from robot.cortex import Cortex
from nanowire_network_simulator import backup, stimulate, Evolution, plot
from os import listdir
from os.path import join, isfile
from scipy.signal import savgol_filter
from analysis import collapse_history, evaluate
from robot.pyramid import Pyramid
from robot.thalamus import Thalamus

DIRECTORY = 'connections/controllers_proximity/'
CONFIGURATION_INDEX = 0
PROXIMITY_MEASURE = True
SENSOR = 'ps1'  # for proximity 'ps6', for distance 'ps1'

IR_RANGE = (65, 1550) if PROXIMITY_MEASURE else (0, 7)
MOTOR_RANGE = (6.28, -6.28) if PROXIMITY_MEASURE else (-6.28, 6.28)

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
chunks = [*map(lambda i: sorted(files[i * 6:][:6]), range(int(len(files) / 6)))]
io_signals = [(chunk[4], chunk[3]) for chunk in chunks]
others = [chunk[:3] + chunk[-1:] for chunk in chunks]
others = list(map(lambda _: backup.read(_[1], _[2], _[3], _[0]), others))

# analyse just one device
io_signals = io_signals[CONFIGURATION_INDEX]
graph, datasheet, wires, connections = others[CONFIGURATION_INDEX]
sensors = connections['inputs']
actuators = connections['outputs']
multipliers = connections['multiplier']
sensitivity = connections['load']


def file_import(name):
    with open(name, 'r') as file:
        return json.loads(file.read())


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
    if not PROXIMITY_MEASURE:
        signals = [s if s < 5 else 5 for s in signals]
    ax.plot(signals, label=key)

if not PROXIMITY_MEASURE:
    labels = [*map(str, range(5))] + ['[7-5]']
    ax.set_yticks(range(len(labels)), labels)
ax.set(title='Sensors readings', xlabel='Iterations', ylabel='Distance')
ax.invert_yaxis()
ax.legend()

# plot direction
ax = next(figs).subplots()

left_signals, right_signals = collapse_history(o_signals).values()
direction = [left - right for left, right in zip(left_signals, right_signals)]
direction = smoother(direction)
ax.plot(direction)
ax.plot([0.0] * len(direction), color='b', linestyle=(0, (5, 5)))
ax.set(title='Robot direction', xlabel='Iterations', ylabel='Direction')
ax.set_yticks(range(-6, 7), ['left', *map(str, range(-10, 11, 2)), 'right'])

# plot motors control signal
axs = iter(next(figs).subplots(1, 2))

for key, command in collapse_history(o_signals).items():
    # approximate signal with a curve; window size 51, polynomial order 3
    command_smooth = smoother(command)
    ax = next(axs)
    ax.plot(command, label='signal')
    ax.plot(command_smooth, color='r', linewidth=3, label='averaged signal')
    ax.set(title=key, xlabel='Iterations', ylabel='Motor speed')
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

ps = collapse_history(i_signals)[SENSOR]
if not PROXIMITY_MEASURE:
    ps = [s if s < 5 else 5 for s in ps]
left = collapse_history(o_signals)['left wheel motor']
right = collapse_history(o_signals)['right wheel motor']

pairs = sorted(zip(ps, left, right))
if not PROXIMITY_MEASURE:
    pairs = [*filter(lambda sd: sd[0] < 5, pairs)]

data = [v for _, v, _ in pairs]
lines = ax.plot(data, color='b', label='left motor')

data = [v for _, _, v in pairs]
lines += ax.plot(data, color='g', label='right motor')
ax.set_ylabel('Motor speed')

ax = ax.twinx()

data = [k for k, *_ in pairs]
lines += ax.plot(data, label=SENSOR, color='r')
ax.set_ylabel('Distance', color='r')

labels = [line.get_label() for line in lines]
ax.legend(lines, labels, loc=0)

plt.title('Sensor-Motor relation for sensor 0')
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
    vmin=-1, vmax=1, cmap='coolwarm'
)
for y, k in enumerate(correlations):
    for x, v in enumerate(correlations[k]):
        plt.text(
            y, x, '%.4f' % v,
            horizontalalignment='center',
            verticalalignment='center',
        )
fig.colorbar(pcm, location='bottom')

plt.title('Sensor-Motor Pearson\'s correlation coefficient')
plt.show()

################################################################################
# ANALYSIS OF MOTOR RESPONSE WITH BROKEN SENSORS (0V INPUT)
# The following graphs show the influence of a missing sensor signal in the
# output computation.
# Since the previous measure of correlation of input and output signals is not
# symptom of a mediating behaviour, the following graph approach an opposite
# analysis. The goal is to understand if the lack/miss of a sensor signal
# effectively/strongly change the behaviour of the robot. This analysis is
# important because allows to understand if the system is controlled by a
# limited number of sensors or if it performs a mediating/mixing process.
# Moreover, it allows to understand the resistance of the system to possible
# damage of components.
# The correlation map on the left gives us an initial and visual idea of the
# relation of input/output signals. It is visible that some sensors influence
# the output more than others, and some greatly influence the final result.
# However, it also shows that, at least for this configuration, no sensors
# completely influence the output and thus that at least a basic mixing process
# is taking place. This is confirmed looking at the changes in the motor outputs
# on the right graphs. We can clearly see that, although the output value may
# increase or decrease, the output signal still follows a similar path.
# The lack/break of a sensor will obviously slightly change the behaviour of the
# robot, but this results show an incredible capacity of possibly manage those
# events. Furthermore, those suggests the possibility of using those measure
# and events also during an offline training, with the aim of maximize the
# resistance to failures. This is however outside the scope of the research,
# that aim instead at an online and continuous training.

# retrieve inputs and outputs nodes
inputs = [(i, 0) for i in sensors.values()]
outputs = {(i, 100) for i in actuators.values()}

cortex = Cortex(graph, datasheet, wires)
pyramid = Pyramid(actuators, sensitivity)
thalamus = Thalamus(sensors, multipliers)


def break_sensor(name: str):
    # reset the network state
    for _ in range(100):
        evaluate(
            cortex, pyramid, thalamus,
            {'ps0': 0.0}, 1e3, IR_RANGE, MOTOR_RANGE
        )

    commands = []
    for stimulus in i_signals:
        stimulus = {k: v for k, v in stimulus.items() if k != name}
        commands += [
            evaluate(
                cortex, pyramid, thalamus,
                stimulus, 0.1, IR_RANGE, MOTOR_RANGE
            )
        ]

    return commands


# stimulate the network disabling each time a different sensor
results = map(break_sensor, [None, *sensors])
normal, *results = map(collapse_history, results)

# calculate correlation between output signals
correlations = [
    {k: 1-stats.pearsonr(normal[k], v)[0] for k, v in dictionary.items()}
    for dictionary in results
]

# remove left/right keys from list
correlations = [[*dictionary.values()] for dictionary in correlations]

fig, other_fig = plt.figure(figsize=(10, 8)).subfigures(1, 2)
left_m_ax, right_m_ax = other_fig.subplots(2, 1)
ax = fig.subplots()

for i, result in enumerate(results + [normal]):
    label, width = (f'ps{i}', 1) if i <= 7 else ('all working', 3)
    left_values = smoother(result['left wheel motor'])
    right_values = smoother(result['right wheel motor'])
    left_m_ax.plot(left_values, label=label, linewidth=width)
    right_m_ax.plot(right_values, label=label, linewidth=width)

left_m_ax.set(title='Left motor behaviour with broken sensors')
left_m_ax.legend(ncol=3)
right_m_ax.set(title='Right motor behaviour with broken sensors')
right_m_ax.legend(ncol=3)

ax.set(title='''
    1 - Pearson\'s correlation coefficient between
    normal and sensor-missing-generated outputs
''')
pcm = ax.pcolormesh(
    actuators.keys(),
    [f'ps{i}' for i in range(8)],
    correlations,
    vmin=-1, vmax=1, cmap='coolwarm'
)
for y, values in enumerate(correlations):
    for x, value in enumerate(values):
        plt.text(
            x, y, '%.4f' % value,
            horizontalalignment='center',
            verticalalignment='center',
        )
fig.colorbar(pcm, location='bottom')

plt.show()

################################################################################
# GRAPHICAL ANALYSIS OF SENSORS CONNECTIONS
# This plot is aimed at better understanding how a good configuration is
# structured in terms of sensors/output connections.
# As visible, the sensors concentrate around the motor that they aim to control
# more. This is likely to change with other tasks that require all the sensors
# to influence the motor output.
# We can see for example that the right sensors tend to organize around the left
# motor, and thus influence it more. This is due to the given configuration,
# that gives an higher motor command for farther obstacles and a low or negative
# value for near obstacles. This organization appears also around the right
# motor, with the only difference of the nearness of the ps0 sensor. This is
# probably due to an internal optimization that helps the robot to run away from
# obstacles, preferring a left turn and thus saving some 'indecision time'.

e = Evolution(datasheet, wires, -1, set(), outputs, [(graph, inputs)])

fig, ax = plt.subplots(figsize=(9.2, 5))
plot.conductance_distribution(fig, ax, e)

# invert dictionary from str -> int to int -> str
labels = {}
for k, v in sensors.items() | actuators.items():
    labels[v] = labels[v] + '/' + k if k in labels else k

nx.draw_networkx_labels(
    graph,
    {
        k: (x, y-4)
        for k, (x, y) in nx.get_node_attributes(graph, 'pos').items()
    },
    labels,
    font_size=18,
    font_color='k'
)

plt.title('Connection and conductivity of the network at its last stimulation')
plt.show()

################################################################################
# CHANGES IN SENSOR-MOTOR PATH RESISTANCE DURING RUN
# This plot shows the variance of the resistance during the robot run. It allows
# to confirm previous observations and to see the influence from the point of
# view of the stimulation of the path.
# Each plot represent the path resistance between the sensor-input nodes and the
# motor node. As we can see, the previous observations are confirmed, in that
# the resistance of near nodes is lower than the one of farther nodes. This
# allows the system to self organize in a way that allows some node to have more
# influence than the others. This is visible by the fact, for example, that
# robot-right sensors have an higher resistance between them and the right
# motor. This observation is opposed but true also for the left motor.
# This graph allows also to observe that there aren't specific nodes that are
# strongly connected with the motor, confirming our previous assertion that the
# output of the motor is a combination of each single sensor signal.
# Finally, this graph shows also the important property of stimulation and
# relaxation. As visible, although the near nodes remain stimulated, the further
# nodes greatly modify their conductance runtime. This is especially visible in
# correspondence of iteration 50, 160, and 280 approximately, where the paths
# are suddenly stimulated by the neighborhood of an obstacle and thus increase
# their conductance.

# reset the network state
for _ in range(100):
    stimulate(graph, datasheet, 1e3, [], [], set())

resistances = []
for i_signal in i_signals:
    evaluate(cortex, pyramid, thalamus, i_signal, 0.1, IR_RANGE, MOTOR_RANGE)
    resistances += [{
        motor_name: {
            sensor_name: nx.resistance_distance(
                graph,
                sensor_index, motor_index,
                weight='Y', invert_weight=False
            )
            for sensor_name, sensor_index in sensors.items()
        }
        for motor_name, motor_index in actuators.items()
    }]

fig = plt.figure(figsize=(10, 8))
axs = fig.subplots(2, 1)

for ax, (motor_name, values) in zip(axs, collapse_history(resistances).items()):
    for sensor_name, resistances in collapse_history(values).items():
        ax.plot(resistances, label=sensor_name)
    ax.set(
        title=f'Sensors to {motor_name} path resistance',
        ylabel='Resistance', yscale='log',
        xlabel='Iteration'
    )
    ax.legend()

fig.suptitle('Change in resistance of sensor-motor path')

plt.subplots_adjust(hspace=0.3)
plt.show()
