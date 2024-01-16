from control.coupling import Coupling
from control.interface import Interface
from control.tsetlin.state import State
from inout.loader import configs
from math import ceil
from nnspy import connected_component
from random import gauss, randrange, sample, choice
from simulation.replica import Replica
from util.evolutor import minimum_distance_selection
from webots.robot import get_actuators, robot, get_sensors

MU = configs["sensors"]["multipliers"]["modification_mu"]
SIGMA = configs["sensors"]["multipliers"]["modification_sigma"]


def adapt(replica: Replica) -> Coupling:

    # decide which coupling will be used at the next epoch
    replica.tsetlin.transit(replica.configuration.performance, replica.history.best_configuration.performance)

    # adapt the best interface known if in ADAPTATION STATE
    if replica.tsetlin.state.type == State.Type.ADAPTATION:
        interface = modify_connections(replica.history.best_configuration.interface.copy(), replica.network.cc)
        interface = modify_multiplier(interface)
    # adapt the last interface if in EXPLORATION STATE
    elif replica.tsetlin.state.type == State.Type.EXPLORATION:
        interface = modify_connections(replica.configuration.interface.copy(), replica.network.cc)
        interface = modify_multiplier(interface)
    # if in OPERATION STATE, copy the best interface
    else:
        interface = replica.history.best_configuration.interface.copy()

    # return the new coupling to use
    return Coupling(interface)


def modify_multiplier(interface: Interface):

    # select the sensor-to-node couplings to re-weight (min 1, max half) from the interface mapping
    reweight_count = randrange(1, ceil(max(interface.c_interface.sources_count * 0.5, 2)))
    couplings = {n: i for n, i in interface.items if n in get_sensors(robot)}
    couplings = sample(couplings.items(), reweight_count)

    # reweight the sensor signal multiplier
    def reweight(pair): return pair[0], (pair[1][0], max(0.0, pair[1][1] + gauss(MU, SIGMA)))
    return Interface(dict(interface.items) | dict(map(reweight, couplings)))


def modify_connections(interface: Interface, component: connected_component) -> Interface:

    # select the sensor-to-node couplings to re-connect (min 1, max half) from the interface mapping
    reconnections_count = randrange(1, ceil(max(interface.c_interface.sources_count * 0.5, 2)))
    couplings = {n: i for n, i in interface.items if n in get_sensors(robot)}
    couplings = sample(couplings.items(), reconnections_count)

    # select the nodes that are at least 2 junctions far from the motor nodes
    # and discard the ones already connected to the sensors
    legal_nodes = minimum_distance_selection(component, set(map(interface.pins.get, get_actuators(robot))), 2)
    legal_nodes -= set(map(interface.pins.get, get_sensors(robot)))

    # reconnect the sensor to a different node by randomly sampling the available ones
    def reconnect(pair): return pair[0], (choice(list(legal_nodes - {pair[1][0]})), pair[1][1])
    return Interface(dict(interface.items) | dict(map(reconnect, couplings)))


__all__ = "adapt",
