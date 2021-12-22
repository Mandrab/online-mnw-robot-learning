import json
import matplotlib.pyplot as plt
import numpy as np

from functools import reduce
from itertools import chain

# from scipy.stats import wilcoxon

# FITNESS = '''[{
#     "density": 2.28,
#     "fitness": [
#         9.893679730051723,
#         9.89591297703065,
#         11.32041228677056,
#         12.344977651989712,
#         9.651836663880779,
#         12.201169204492736,
#         41.55280356272701,
#         56.08487974424363,
#         61.051341997897275,
#         63.692826600760576,
#         62.690962478250256,
#         12.665865427347866,
#         9.680567497221322,
#         52.927749012298115,
#         11.629956505940207,
#         38.592685600319115,
#         52.30647705168202,
#         63.13167338271604,
#         10.380993239484749,
#         38.62662226839331,
#         9.754733969688983,
#         60.52296781925107,
#         9.6982368822096,
#         68.93608202294246,
#         16.585496771493805,
#         14.706265247179426,
#         67.16591088683936,
#         34.85062790525828,
#         64.11392211534813,
#         70.47171178937148,
#         9.849041638610927
#     ]
# }, {
#     "density": 4.36,
#     "fitness": [
#         68.18415288098598,
#         52.64649676815236,
#         61.7853608143593,
#         69.84014048433215,
#         69.12291474688014,
#         11.800360265897481,
#         19.87896641492256,
#         70.28835807812449,
#         9.725444029860734,
#         71.29283163524012,
#         52.150364992710536,
#         70.7237702283475,
#         66.68856917015408,
#         62.33236285872705,
#         11.840695875808082,
#         12.748019468513053,
#         62.45866690934977,
#         67.02824987070473,
#         69.02146532790613,
#         10.449178365557207,
#         49.703413259981886,
#         58.80667240630984,
#         53.7963114937628,
#         57.98198894810026,
#         66.36390490839982,
#         9.824803250984424,
#         69.12095718309179,
#         9.61570543859205,
#         70.30702784751934,
#         71.12020613653408,
#         60.21853868130751
#     ]
# }, {
#     "density": 5.84,
#     "fitness": [
#         9.655299936413023,
#         12.48738523590077,
#         9.915328576178942,
#         9.55446288121629,
#         11.207857117301755,
#         9.864942439295092,
#         9.830595231124185,
#         14.870930757093129,
#         10.06094422597965,
#         12.006263402256623,
#         24.904808281318793,
#         9.73642232190627,
#         11.629335944597512,
#         9.714408133677987,
#         12.150507732646965,
#         11.99615627992474,
#         16.775661095031317,
#         12.144827101623335,
#         11.621207343571877,
#         16.049405174104894,
#         23.067061180621756,
#         46.01942316102641,
#         49.83726330214995,
#         11.47022629871017,
#         9.860075835429697,
#         20.079569716412387,
#         11.324646282852571,
#         48.66502378610563,
#         32.04977843926219,
#         41.96236645544552,
#         27.04368866791387
#     ]
# }, {
#     "density": 8.16,
#     "fitness": [
#         10.868690659245932,
#         9.6968521398688,
#         52.32529813139484,
#         55.70116508382489,
#         42.25119896010621,
#         9.905026228498901,
#         17.974544157475215,
#         30.139641388719035,
#         55.530219066386756,
#         42.44754926914011,
#         59.73328779247671,
#         50.29762204525841,
#         9.699171752021902,
#         34.922580000126864,
#         26.713070929575917,
#         9.77104549316129,
#         44.38347599374058,
#         54.82943763620082,
#         10.6112698525717,
#         48.20157046921074,
#         10.439766709167657,
#         15.684251363590738,
#         9.805420328231465,
#         54.0859373225739,
#         9.921530992771244,
#         9.702023152426333,
#         45.5265414221202,
#         21.098069747791794,
#         59.283286949252286,
#         14.292213815702313,
#         60.81505096313158
#     ]
# }]'''
#
# fig = plt.figure(figsize=(10, 6))
# fig1, fig2 = fig.subfigures(1, 2, width_ratios=[2, 1])
# ax1, ax2 = fig1.subplots(), fig2.subplots()
# ax1.set(
#     title='Fitness according to network creation densities',
#     xlabel='Configuration', ylabel='Fitness'
#
# )
#
# for dictionary in densities:
#     density = dictionary['density']
#     fitness = sorted(dictionary['fitness'])
#     ax1.plot(fitness, label=f'density {density}')
#
# ax1.legend()
#
# ax2.set(title='''
#     Wilcoxon P-values
#     between fitness distributions
#     black: < 0.05; yellow: > 0.05
# ''')
# # todo wtf
# p_values = [
#     [
#         wilcoxon(d1['fitness'], d2['fitness']).pvalue > 0.05
#         if d1 is not d2 else 0
#         for d2 in densities
#     ]
#     for d1 in densities
# ]
# ticks = [d['density'] for d in densities]
# ax2.set(xticks=ticks, yticks=ticks)
# pcm = ax2.pcolormesh(ticks, ticks, p_values)
# fig2.colorbar(pcm, location='bottom')
#
# plt.subplots_adjust(top=0.8, bottom=0.1, hspace=0.4)
# plt.show()

################################################################################
# DENSITY INFLUENCE ON FITNESS

with open('fitness_1.json') as file:
    data = json.load(file)

fig = plt.figure(figsize=(10, 10))
fig.suptitle('Fitness according to network creation densities')

ax1, ax2 = fig.subplots(2, 1)

densities_keys = sorted(set(map(lambda _: _['density'], data)))


def _(f=lambda _: _):
    return dict(map(
        lambda k: (k, reduce(
            lambda a, b: a + [f(b['fitness'])],
            filter(lambda _: _['density'] == k, data),
            list()
        )),
        densities_keys
    ))


densities = {k: [*chain(*v)] for k, v in _().items()}
ax1.boxplot(densities.values())

densities = [None] + [np.percentile(v, 50) for v in densities.values()]
ax1.plot(densities, linewidth=3, linestyle='dotted')

ax1.set(title='All fitness history', xlabel='Density', ylabel='Fitness')
ax1.set_xticks(
    [*range(len(densities_keys) + 2)],
    labels=[3.5, *densities_keys, 9.5]
)
ax1.yaxis.grid(True, linestyle='dotted')

ax2.boxplot(_(max).values())

densities = [None] + [np.percentile(v, 50) for v in _(max).values()]
ax2.plot(densities, linewidth=3, linestyle='dotted')

ax2.set(title='Max fitness', xlabel='Density', ylabel='Fitness')
ax2.set_xticks(
    [*range(len(densities_keys) + 2)],
    labels=[3.5, *densities_keys, 9.5]
)
ax2.yaxis.grid(True, linestyle='dotted')

plt.tight_layout()
plt.show()
