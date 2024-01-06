from config import *
from ctypes import c_double, c_int
from nnspy import nns, interface
from optimization.simulation import optimize
from optimization.utils import import_simulations, new_simulations


# import simulations from the 'controllers' folder
simulations = import_simulations(robot, simulation_settings)

# if no simulations have been imported, generate new ones
if not simulations:
    simulations = new_simulations(robot, simulation_settings, settings)

# run simulations of different devices and save the best scoring configurations
for index, individual in enumerate(map(optimize, simulations)):
    file_format = str(save_path) + '/{name}' + f'.{index}.dat'

    it = interface()
    it.sources_count = len(individual.elite.thalamus.mapping)
    it.sources_index = (c_int * it.sources_count)()
    it.grounds_count = 0
    it.grounds_index = (c_int * it.grounds_count)()
    it.loads_count = len(individual.elite.pyramid.mapping)
    it.loads_index = (c_int * it.loads_count)()
    it.loads_weight = (c_double * it.loads_count)()

    ios = (c_double * it.sources_count)()

    for i, pin in enumerate(individual.elite.pyramid.mapping.values()):
        it.loads_index[i] = pin
        it.loads_weight[i] = individual.elite.pyramid.sensitivity

    for i, pin in enumerate(individual.elite.thalamus.mapping.values()):
        it.sources_index[i] = pin

    nns.serialize_network(individual.elite.cortex.datasheet, individual.elite.cortex.topology, ".".encode('utf-8'), index)
    nns.serialize_state(individual.elite.cortex.datasheet, individual.elite.cortex.topology, individual.elite.cortex.state, ".".encode('utf-8'), index, 0)
    nns.serialize_component(individual.elite.cortex.component, ".".encode('utf-8'), index, 0)
    nns.serialize_interface(it, ".".encode('utf-8'), index, 0)

# end of the simulation
logger.info('Simulation complete')
