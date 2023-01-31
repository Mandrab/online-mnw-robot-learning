from config import *
from optimization.simulation import optimize
from optimization.utils import import_simulations, new_simulations, save


# import simulations from the 'controllers' folder
simulations = import_simulations(robot, simulation_settings)

# if no simulations have been imported, generate new ones
if not simulations:
    simulations = new_simulations(robot, simulation_settings, settings)


# run simulations of different devices and save the best scoring configurations
for index, individual in enumerate(map(optimize, simulations)):
    file_format = str(save_path) + '/{name}' + f'.{index}.dat'
    save(individual.elite, file_format)


# end of the simulation
logger.info('Simulation complete')
