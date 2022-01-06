import os

from config import *
from datetime import datetime
from optimization.simulation import optimize
from optimization.utils import import_simulations, new_simulations, save


# create the folder for saving the simulation files
CONFIGURATIONS_LOCATION = '../../res/configuration'
SAVING_FOLDER = datetime.today().strftime('%Y-%m-%d.%H%M%S%f')
os.mkdir(path := os.path.join(CONFIGURATIONS_LOCATION, SAVING_FOLDER))


# import simulations from the 'controllers' folder
simulations = import_simulations(robot, simulation_settings)

# if no simulations have been imported, generate new ones
if not simulations:
    simulations = new_simulations(robot, simulation_settings, settings)


# run simulations of different devices and save the best scoring configurations
for index, individual in enumerate(map(optimize, simulations)):
    file_format = str(path) + '/{name}' + f'.{index}.dat'
    save(individual.elite, file_format)


# end of the simulation
logger.info('Simulation complete')
robot.simulationQuit(0)
