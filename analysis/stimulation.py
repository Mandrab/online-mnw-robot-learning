import matplotlib.pyplot as plt
import networkx as nx

from analysis import *
from nanowire_network_simulator import Evolution

fig, axs = plt.subplots(1, 3, figsize=(12, 4))

for ax, frequency in zip(axs, [0.1, 2, 10]):
    inputs = map(lambda _: max(sensor_range) / _, range(1, 6))
    colors = iter(['b', 'g', 'c', 'm', 'y'])
    line = []

    for i in inputs:
        cortex, pyramid, thalamus = generate(load=100, seed=1234)
        loads = {(a, pyramid.sensitivity) for a in nodes(pyramid.mapping)}
        e = Evolution(default_datasheet, dict(), 0.1, loads=loads)

        for _ in (s := [i] * 20 + [0] * 30):
            evaluate(cortex, pyramid, thalamus, {'s': _}, frequency)
            stimulus = adapt(_, sensor_range, (0, 10))
            e.append(cortex.network, [(thalamus.mapping['s'], stimulus)])

        conductances = [1 / nx.resistance_distance(
            network,
            thalamus.mapping['s'], pyramid.mapping['m'],
            weight='Y', invert_weight=False
        ) for network, _ in e.network_instances]

        ax.set_xlabel('time (s)')
        ax.set_ylabel('Input Voltage (V)', color='tab:red')
        ax.tick_params(axis='y', labelcolor='tab:red')
        line += ax.plot([adapt(_, sensor_range, (0, 10)) for _ in s], color='r')

        ax1 = ax.twinx()

        ax1.set_ylabel('Conductance (S)')
        ax1.set_ylim([0, 0.0663])
        label = f"{adapt(i, sensor_range, (0, 10)):.2f} V"
        line += ax1.plot(conductances, label=label, color=next(colors))

    plt.legend(line, [_.get_label() for _ in line], loc=0)
    plt.title(f'Conductance with {1 / frequency}Hz stimulus')

plt.suptitle('Stimulus and frequency influence on the conductance')
plt.tight_layout()
plt.show()
