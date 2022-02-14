import json
import matplotlib.patches as ptc

from fitness import *
from itertools import chain
from scipy.signal import savgol_filter


with open('fitness.2022.02.02.json') as file:
    data = json.load(file)

################################################################################
# DATA STATISTICS
# Measures about fitness. TODO data may be to low

statistics(data, 'density')
statistics(data, 'load')

################################################################################
# ITERATIONS INFLUENCE ON FITNESS
# It is visible that higher density networks tend to improve more their fitness.
# This is probably due to the fact that the larger space of solution, although
# complicating the search, allows for more optimised configurations. The
# optimisation of smaller networks may indeed be more related to lucky
# configurations. This hypothesis is due to the more abrupt improvements at some
# iterations. Note that the fitness is calculated as the

fig, ax = plt.subplots()

groups = group(data, 'density', 'fitness')
groups = list(zip(groups.items(), ['tab:blue', 'tab:red', 'tab:green']))

for (k, v), c in groups:
    iteration_count = len(v[0])

    for i in range(iteration_count):
        fitness = list(map(max, [_[:i + 1] for _ in v]))
        average = sum(fitness) / len(fitness)

        ax.plot(i, average, 'o', markersize=1, color=c, label=k)

plt.title('Fitness evolution according to iterations')
patches = [ptc.Patch(color=c, label=f'density {k}') for (k, _), c in groups]
plt.legend(handles=patches, loc='lower right')
plt.show()

################################################################################
# DENSITY INFLUENCE ON FITNESS
# The creation density seems to not influence the average results particularly.
# Nevertheless it influence the final fitness, restricting the range toward
# higher values. It also seems to almost always guarantee a completion of the
# task, considering the threshold as 45.0 TODO. This is not true for lower
# creation densities. The hypothesis is thus that less dense networks may be
# more dependent on lucky-creations than denser networks are.
#
# note that the multiplier may influence; the fitness threshold to 40 may limit.

groups = group(data, 'density', 'fitness').items()

title = 'Fitness distribution according to network creation densities'
boxplot(title, 'Density', 'Fitness', {k: [*chain(*v)] for k, v in groups})

title = 'Max fitness distribution according to network creation densities'
boxplot(title, 'Density', 'Fitness', {k: [*map(max, v)] for k, v in groups})

################################################################################
# LOAD INFLUENCE ON FITNESS
# Lower loads, whose make the network more sensible, seems to slightly improve
# the performances. This is consistent with the hypothesis, in that the success
# of the task requires the network to be sensible to stimulations and to
# maintain the sensitivity in time. This last point is simplified by low loads,
# in that the network will be less subject to relaxation.
#
# note that the multiplier may influence

groups = group(data, 'load', 'fitness').items()

title = 'Fitness distribution according to connected motor loads'
boxplot(title, 'Load', 'Fitness', {k: [*chain(*v)] for k, v in groups})

title = 'Max fitness distribution according to connected motor loads'
boxplot(title, 'Load', 'Fitness', {k: [*map(max, v)] for k, v in groups})

################################################################################
# DENSITY + LOAD INFLUENCE ON FITNESS
# The evaluation of loads influence according to the density helps to understand
# how and in which condition they impact on the results. It seems that for low
# densities, low loads performs better. This is due to the fact that the network
# is less (???) resistive, and thus lower loads allows it to be more stimulated.
# This lose importance for higher densities. TODO why?
#
# note there are just 5 data for each configuration, consider use also other
# runs results

fig, axs = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Max fitness distribution according to connected motor loads')

for ax, (k, v) in zip(axs, group(data, 'density').items()):
    groups = group(v, 'load', 'fitness').items()
    groups = {k: [*map(max, v)] for k, v in groups}
    ax.boxplot(groups.values())

    labels = [None, *map("{:.2e}".format, groups), None]
    ax.set_xticks([*range(len(groups) + 2)], labels=labels)
    ax.yaxis.grid(True, linestyle='dotted')

    ax.set(xlabel='Fitness', ylabel='Ground/proximity sensor ratio')
    ax.set_title(f'Density {k}')

plt.tight_layout()
plt.show()

################################################################################
# MULTIPLIERS INFLUENCE ON FITNESS
# The performances does not seems to be strictly related with the ratio between
# ground and proximity sensors. Nevertheless, low scores seem to always be
# connected with higher ratios (i.e., when the ground sensor is more influential
# than the proximity one). Contrarily, high scores are related to lower ratios.
# No explanation has been found for this behaviour.

for i, d in enumerate(data):
    with open(f'2022-02-02.182838773520/connections.{i}.dat') as file:
        file_data = json.load(file)
        d['multiplier'] = file_data['multiplier']


def avg(m): return 2 * m['gs0'] / (m['ps0'] + m['ps7'])


groups = {
    k: sorted([(max(v['fitness']), avg(v['multiplier'])) for v in vs])
    for k, vs in group(data, 'density').items()
}

fig, axs = plt.subplots(1, 3, figsize=(15, 5))
for (k, vs), ax in zip(groups.items(), axs):
    fitness, multiplier = [k for k, _ in vs], [v for _, v in vs]
    ax.plot(fitness, multiplier, label='raw')
    ax.plot(fitness, savgol_filter(multiplier, 19, 3), label=f'smoothed')
    ax.set(xlabel='Fitness', ylabel='Ground/proximity sensor ratio')
    ax.set_title(f'Density {k}')
    ax.legend()

fig.suptitle('Fitness distribution according ground/proximity sensor ratio')
plt.show()
