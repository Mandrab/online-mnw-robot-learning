import json
import sys

from fitness import *
from scipy.signal import savgol_filter


with open(sys.argv[1] + 'dataset.json') as file:
    data = json.load(file)

if 'area' in sys.argv[1]:
    limits = [75, 90]
elif 'collision' in sys.argv[1]:
    limits = [50]
elif 'tmaze' in sys.argv[1]:
    limits = [40, 50]
else:
    raise Exception('range unknown')

################################################################################
# DATA STATISTICS
# Measures about fitness. TODO data may be to low

statistics(data, 'density', limits)
statistics(data, 'load', limits)

################################################################################
# ITERATIONS INFLUENCE ON FITNESS - DENSITY
# It is visible that higher density networks tend to improve more their fitness.
# This is probably due to the fact that the larger space of solution, although
# complicating the search, allows for more optimised configurations. The
# optimisation of smaller networks may indeed be more related to lucky
# configurations. This hypothesis is due to the more abrupt improvements at some
# iterations. Note that the fitness is calculated as the average of maximums

evolutions(data, 'density')

################################################################################
# ITERATIONS INFLUENCE ON FITNESS - LOADS
# Differently from the evolution of the density, the load seems to impact less
# on the fitness. The only conclusion is that lower loads seems to perform
# slightly better that higher ones. Nevertheless, due to the reduced population
# (15?) this result may not be completely valid. Note that the fitness is
# calculated as the average of maximums

evolutions(data, 'load')

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

groups = group(data, 'density', 'fitness')

title = 'Fitness distribution according to network creation densities'
boxplot(title, 'Density', 'Fitness', evolution(groups))

################################################################################
# LOAD INFLUENCE ON FITNESS
# Lower loads, whose make the network more sensible, seems to slightly improve
# the performances. This is consistent with the hypothesis, in that the success
# of the task requires the network to be sensible to stimulations and to
# maintain the sensitivity in time. This last point is simplified by low loads,
# in that the network will be less subject to relaxation.
#
# note that the multiplier may influence

groups = group(data, 'load', 'fitness')

title = 'Fitness distribution according to motor loads'
boxplot(title, 'Load', 'Fitness', evolution(groups))

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
fig.suptitle(
    'Max fitness distribution according to ' +
    'network creation density and connected motor loads'
)

for ax, (k, v) in zip(axs, group(data, 'density').items()):
    groups = group(v, 'load', 'fitness').items()
    groups = {k: [*map(max, v)] for k, v in groups}
    ax.boxplot(groups.values())

    labels = [None, *map("{:.2e}".format, groups), None]
    ax.set_xticks([*range(len(groups) + 2)], labels=labels)
    ax.yaxis.grid(True, linestyle='dotted')

    ax.set(xlabel='Load', ylabel='Fitness')
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

if 'tmaze' not in sys.argv[1]:
    exit()

for i, d in enumerate(data):
    with open(f'{sys.argv[1]}/connections.{i}.dat') as file:
        file_data = json.load(file)
        d['multiplier'] = file_data.get('multiplier', 1.0)


def proportion(m): return 2 * m['gs0'] / (m['ps0'] + m['ps7'])


groups = {
    k: sorted([(max(v['fitness']), proportion(v['multiplier'])) for v in vs])
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
