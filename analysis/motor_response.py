import matplotlib.pyplot as plt

from nanowire_network_simulator import plot, Evolution
from nanowire_network_simulator.model.device import Datasheet as Ds
from analysis import *


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


def __influence(values):
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(7, 16))
    values_ax, *axs = axs

    for ax, s in zip(axs, values):
        # avoid modify the graph
        cortex, thalamus = generate(load=100, seed=1234)
        def step(i): return evaluate(cortex, thalamus, {'s': i}, s)

        io = {
            i: [v for v in step(i).values()][0]
            for i in range(*sensor_range, 128)
        }

        # make data
        x = [*io.keys()]
        y = [*io.values()]

        values_ax.plot(x, y, label=f'frequency {1.0 / s} Hz')

        e = Evolution(
            default_datasheet,
            wires_dict={}, delta_time=s, grounds=set(),
            loads={(a, 1) for a in thalamus.motors.values()},
            network_instances=[(
                cortex.network,
                [(s, sensor_range[1]) for s in thalamus.sensors.values()]
            )]
        )

        plot.conductance_distribution(fig, ax, e)
        ax.set_title(f'Conductance in {1 / s} Hz updated network')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.subplots_adjust(top=0.95, bottom=0.03, hspace=0.4)

    plt.suptitle(
        'Analysis of the update frequency influence in the signal propagation'
    )
    plt.show()


__influence([0.1, 5, 10])


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

def __influence(values):
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(7, 16))
    values_ax, *axs = axs

    for ax, value in zip(axs, values):
        # avoid modify the graph
        cortex, thalamus = generate(load=value, seed=1234)
        def step(i): return evaluate(cortex, thalamus, {'s': i}, 0.1)

        io = {
            i: [v for v in step(i).values()][0]
            for i in range(*sensor_range, 128)
        }

        # make data
        x = [*io.keys()]
        y = [*io.values()]

        values_ax.plot(x, y, label=f'resistance {value} Ohm')

        e = Evolution(
            default_datasheet,
            wires_dict={}, delta_time=value, grounds=set(),
            loads={(a, value) for a in thalamus.motors.values()},
            network_instances=[
                (cortex.network, [
                    (s, sensor_range[1])
                    for s in thalamus.sensors.values()
                ])
            ])

        plot.conductance_distribution(fig, ax, e)
        ax.set_title(f'Conductance in network with {value} Ohm load')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.subplots_adjust(top=0.95, bottom=0.03, hspace=0.4)
    plt.suptitle(
        'Analysis of the motor resistance influence in the signal propagation'
    )
    plt.show()


__influence([1, 100, 10000])


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

def __influence(values):
    fig, axs = plt.subplots(len(values) + 1, 1, figsize=(7, 16))
    values_ax, *axs = axs

    for ax, value in zip(axs, values):
        cortex, thalamus = generate(value, load=50)
        def step(i): return evaluate(cortex, thalamus, {'s': i}, 0.1)

        io = {
            i: [v for v in step(i).values()][0]
            for i in range(*sensor_range, 128)
        }

        # make data
        x = [*io.keys()]
        y = [*io.values()]

        values_ax.plot(x, y, label=f'wires {value.wires_count}')

        e = Evolution(
            default_datasheet,
            wires_dict={}, delta_time=value, grounds=set(),
            loads={(a, value) for a in thalamus.motors.values()},
            network_instances=[
                (cortex.network, [
                    (s, sensor_range[1])
                    for s in thalamus.sensors.values()
                ])
            ])

        plot.conductance_distribution(fig, ax, e)
        ax.set_title(f'Conductance in network with {value.wires_count} wires')

    values_ax.set(xlabel='Sensors signals', ylabel='Motor outputs')
    values_ax.legend()

    plt.subplots_adjust(top=0.95, bottom=0.03, hspace=0.4)
    plt.suptitle(
        'Analysis of the wires density influence in the signal propagation'
    )
    plt.show()


__influence([
    Ds(wires_count=100, Lx=30, Ly=30, mean_length=10, std_length=10 * 0.35),
    Ds(wires_count=300, Lx=30, Ly=30, mean_length=10, std_length=10 * 0.35),
    Ds(wires_count=500, Lx=30, Ly=30, mean_length=10, std_length=10 * 0.35)
])
