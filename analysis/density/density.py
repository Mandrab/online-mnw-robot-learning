import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import sys

from functools import reduce
from itertools import chain
from scipy.stats import wilcoxon


def list_to_dict(data_dict, keys, f=lambda _: _):
    return dict(map(
        lambda k: (k, reduce(
            lambda a, b: a + [f(b['fitness'])],
            filter(lambda _: _['density'] == k, data_dict),
            list()
        )),
        keys
    ))


################################################################################
# EVOLUTION HISTORIES SIMILARITY

ALPHA_PARAMETER = 0.05

with open(f'density/fitness.mw1.20211212.141649.json') as file:
    data = json.load(file)

fig = plt.figure(figsize=(10, 6))
figs = iter(fig.subfigures(1, 2, width_ratios=[2, 1]))

ax = next(figs).subplots()

densities = sorted(set(map(lambda _: _['density'], data)))
densities = {k: [*chain(*v)] for k, v in list_to_dict(data, densities).items()}

for density in densities:
    fitness = sorted(densities[density]) # todo
    ax.plot(fitness, label=f'density {density}')

ax.set(
    title='Fitness according to network creation densities',
    xlabel='Configuration', ylabel='Fitness'
)
ax.legend()

fig = next(figs)
ax = fig.subplots()

min_length = min([len(v) for k, v in densities.items()])
densities = {k: v[:min_length] for k, v in densities.items()}
p_values = [
    [
        wilcoxon(densities[d1], densities[d2]).pvalue < ALPHA_PARAMETER
        if d1 is not d2 else False
        for d2 in densities
    ]
    for d1 in densities
]
ticks = list(densities.keys())
ax.pcolormesh(ticks, ticks, p_values)
sm = cm.ScalarMappable()
sm.set_array([0, ALPHA_PARAMETER])
fig.colorbar(sm, location='bottom')
ax.set(
    title='Wilcoxon P-values\nbetween fitness distributions',
    xticks=ticks, yticks=ticks
)

plt.show()

################################################################################
# DENSITY INFLUENCE ON FITNESS
# This plots shows the influence of the density in the achievement of a good
# fitness in the same task.
# It is visible that the density has a really low impact on the score obtained
# by the robot in the same task. This is also visible by the notch, that indeed
# tell us that we cannot say that the medians of the distributions are different
# (todo, i think we cannot say that they are equals).
# The hypothesis however is that this results would change in case of more
# complicated tasks.

_0, fitness_file_name, *_1 = *sys.argv, None
fitness_file_name = fitness_file_name or 'fitness.mw1.20211220.153556'

with open(f'density/{fitness_file_name}.json') as file:
    data = json.load(file)

fig = plt.figure(figsize=(10, 10))
fig.suptitle('Fitness according to network creation densities')
axs = iter(fig.subplots(2, 1))

ax = next(axs)

keys = sorted(set(map(lambda _: _['density'], data)))
densities = {k: [*chain(*v)] for k, v in list_to_dict(data, keys).items()}
ax.boxplot(densities.values(), notch=True)

densities = [None] + [np.percentile(v, 50) for v in densities.values()]
ax.plot(densities, linewidth=3, linestyle='dotted')

ax.set(title='All fitness history', xlabel='Density', ylabel='Fitness')
ax.set_xticks(
    [*range(len(keys) + 2)],
    labels=[3.5, *keys, 9.5]
)
ax.yaxis.grid(True, linestyle='dotted')

ax = next(axs)
ax.boxplot(list_to_dict(data, keys, max).values(), notch=True)

densities = [None] + [
    np.percentile(v, 50) for v in list_to_dict(data, keys, max).values()
]
ax.plot(densities, linewidth=3, linestyle='dotted')

ax.set(title='Max fitness', xlabel='Density', ylabel='Fitness')
ax.set_xticks([*range(len(keys) + 2)], labels=[3.5, *keys, 9.5])
ax.yaxis.grid(True, linestyle='dotted')

plt.tight_layout()
plt.show()
