import matplotlib.patches as ptc
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from analysis import *
from nanowire_network_simulator import plot, Evolution
from nanowire_network_simulator.model.device import Datasheet as Ds
from typing import List, Callable, Any


################################################################################
# UTILITIES

def influence(
        superior_title: str,
        title_supplier: Callable[[Any], str],
        labeler: Callable[[Any], str],
        xye_supplier: Callable[[Any], Tuple[
            Iterable[float], Iterable[Dict[str, float]], Evolution]
        ],
        values: List[Any],
        detailers: List[Callable[[Any, Any, Evolution], None]]
):
    """
    Plot graphs to represent the influence of a specific parameter on the output
    signal to control the motor.
    """

    def apply(v: Any): return *xye_supplier(v), labeler(v), title_supplier(v)
    values, count = list(map(apply, values)), len(values)

    _, ax_ = plt.subplots()
    for x_, y_, _0, label_, _1 in values:
        ax_.plot(list(range(len(y_))), y_, label=label_)
    ax_.set(xlabel='Iteration', ylabel='Motor rotation speed (rad/s)')
    ax_.legend()
    ax_ = ax_.twinx()
    ax_.plot(x_, color='tab:red', linestyle=(0, (1, 10)), linewidth=2.5)
    ax_.set_ylabel('Voltage (V)', color='tab:red')
    ax_.tick_params(axis='y', colors='tab:red')
    plt.suptitle(superior_title)
    plt.tight_layout()
    plt.show()

    def details(detailer_function):
        fig = plt.figure(figsize=(5 * count, 5))
        axs = map(lambda _: plt.subplot(1, count, _), range(1, 1 + count))
        for ax, (x, y, e, label, title) in zip(axs, values):
            detailer_function(fig, ax, e)
            ax.set_title(title)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.05, top=0.85)
        plt.suptitle(superior_title)
        plt.show()
    list(map(details, detailers))


def stimulation_values(
        cortex: Cortex,
        pyramid: Pyramid,
        thalamus: Thalamus,
        time: float = 0.1
) -> Tuple[Iterable[float], Iterable[Dict[str, float]], Evolution]:
    """
    Stimulate the network and return the sequence of outputs signals and the
    evolution dataclass.
    """

    loads = {(a, pyramid.sensitivity) for a in nodes(pyramid.mapping)}
    e = Evolution(default_datasheet, dict(), time, loads=loads)

    def step(i):
        output = evaluate(cortex, pyramid, thalamus, {'s': i}, time)
        stimulus = [(thalamus.mapping['s'], adapt(i, sensor_range, (0, 10)))]
        e.append(cortex.network, stimulus)
        return output

    io = {
        i: [v for v in step(i).values()][0]
        for i in range(*sensor_range, 128)
    }

    # make data
    x: List[float] = [adapt(s, sensor_range, (0, 10)) for s in io.keys()]
    y: List[Dict[str, float]] = [*io.values()]

    return x, y, e


################################################################################
# RESPONSE ANALYSIS IN FREQUENCY CHANGES
# The following graphs shows the variance of the motor output, in a random
# connection, according to an increasing sensor input at different frequencies.
# When the frequency is high, the network is frequently stimulated and the best
# path decrease its resistance more than the others (the voltage is subdivided
# between less, and thus highly stimulated, nano-wires):
#   10v ---/\/\/\--- 5v ---/\/\/\--- 0v
#         stim. 5v        stim. 5v
#   10v ---/\/\/\--- 6.6v ---/\/\/\--- 3.3v ---/\/\/\--- 0v
#        stim. 3.3v        stim. 3.3v        stim. 3.3v
# When the frequency is low, the path relax after each stimulation and only the
# source-neighbor arches become conductive. That due to the fact that the
# network behaves like a parallel circuit. Normally, the further we go from the
# source, the more parallel it becomes. This lower the overall resistance at
# lower levels and makes those subject to lesser stimulus. With high frequencies
# the first node resistance decrease more and move some of the stimulus to the
# following resistances. In lower frequencies however, the nano-wires relax and
# this property vanish, making only the source-neighbor arches highly
# conductive.
#                      ---/\/\/\---
#                     |           |
#   10v ---/\/\/\--- 6.6v         0v
#                    |           |
#                    ---/\/\/\---
#                    ---/\/\/\---
#                   |           |
#   10v ---/\/\--- 5v         0v    HIGH FREQ
#                  |           |
#                  ---/\/\/\---
#   FOR LOW FREQ. THE FIRST ARCH HAS TIME TO RELAX
# This behaviour make the output higher in the first case, in that the path
# resistance decrease more homogeneously and, overall, more. The voltage delta
# move then towards the load, that has instead a fixed resistance, making the
# output higher.
# This analysis suggests that high frequently updated network are more likely to
# change their behaviour runtime due to the higher number of highly-variable
# wires, possibly increasing capabilities.

counter: int = 0


def detailer(fig, ax, e: Evolution):
    """Plot the conductance distribution at penultimate state"""
    e = Evolution(
        e.datasheet, e.wires_dict, e.delta_time, e.grounds, e.loads,
        [e.network_instances[-2]]
    )
    plot.conductance_distribution(fig, ax, e)


influence(
    'Analysis of the update frequency influence in the signal propagation',
    lambda s: f'Conductance in {1 / s} Hz updated network',
    lambda s: f'frequency {1.0 / s} Hz',
    lambda s: stimulation_values(*generate(load=100, seed=1234), time=s),
    values=[0.1, 5, 10],
    detailers=[
        plot.conductance_distribution, detailer, plot.network_conductance
    ]
)


################################################################################
# RESPONSE ANALYSIS IN LOAD CHANGES
# The following graphs show the influence of the motor resistance in the
# stimulation of the network.
# When the resistance is low, just a small amount of tension 'fall' at the sides
# of the motor. This cause the network to be highly stimulated, in that the vast
# majority of the tension falls inside the device.
# Differently, when the device is connected to an 'heavy' load, an high voltage
# is measurable at the sides of the motor. This makes the network just softly
# stimulated, and prevents any interesting plasticity to show-up.
# It is also interesting to note that an high load directly influences the motor
# speed. Indeed, an higher voltage will insists on the motor, making it move
# fastly.
# The said properties are opposite: high plasticity brings to low speed; low
# plasticity to high speed. Given a complex system that need both, a solution
# may consists in the adjustment of the output value to a specific range.
# This may be achieved through the connection of a transistor and a carefully
# chosen resistance as to allow the control with higher voltages. This would
# however complicate the hardware solution. A more evolutionary oriented ways is
# to find a balance of the two properties.

influence(
    'Analysis of the motor resistance influence in the signal propagation',
    lambda _: f'Conductance in network with {_} Ohm load',
    lambda _: f'resistance {_} Ohm',
    lambda _: stimulation_values(*generate(load=_, seed=1234)),
    values=[1, 100, 10000],
    detailers=[plot.conductance_distribution, plot.network_conductance]
)


################################################################################
# RESPONSE ANALYSIS IN DENSITY CHANGES
# The following charts show the changes in the network behaviour at the increase
# of the nano-wires density.
# With an high density, the emergence of well defined paths decrease. This is
# due to the fact that the density means an increase in the number of nano-wires
# (i.e. resistances) in the device. This is comparable with an electronic
# circuit with parallel resistors: the more, the lower the overall resistance
# become. This characteristic collides with the fixed load's resistance, moving
# a percentage of the voltage fall at the sides of the motor.
# Following the same reasoning used for the load's resistance, this property
# implies that an increment in the network density will cause an increase in the
# output value and a consequently decrease in the network plasticity. The choose
# of a correct density should then seek for a balance between the output values
# and the network plasticity.

datasheets = [
    Ds(wires_count, Lx=30, Ly=30, mean_length=10, std_length=10 * 0.35)
    for wires_count in [100, 300, 500]
]


def detailer(fig, ax, e: Evolution):
    plot.network_conductance(fig, ax, e)
    xs = [i * 0.1 for i in range(len(e.network_instances))]
    avg_conductance = [
        sum(g[a][b]['Y'] for a, b in g.edges) / g.number_of_edges()
        for g, _ in e.network_instances
    ]
    ax = fig.axes[-1]
    ax.plot(xs, avg_conductance, color='y')

    patches = [
        ptc.Patch(color='r', label='Input voltage'),
        ptc.Patch(color='b', label='Network conductance'),
        ptc.Patch(color='y', label='Average nodes conductance')
    ]
    ax.legend(handles=patches, loc='upper left')
    plt.yscale('log', base=2)
    ax.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.3f'))


influence(
    'Analysis of the wires density influence in the signal propagation',
    lambda _: f'Conductance in network with {_.wires_count} wires',
    lambda _: f'wires {_.wires_count}',
    lambda _: stimulation_values(*generate(_, load=50), time=0.1),
    values=datasheets,
    detailers=[plot.conductance_distribution, detailer]
)
