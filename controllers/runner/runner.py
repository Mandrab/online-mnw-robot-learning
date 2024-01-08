from config import logger, robot, settings, simulation_settings
from optimization.simulation import optimize
from optimization.simulations import new_simulations, save

# generate new simulations
simulations = new_simulations(robot, simulation_settings, settings)

# run simulations of different devices and save the best scoring configurations
list(map(save, enumerate(map(lambda s: s.elite, map(optimize, simulations)))))

# end of the simulation
logger.info('Simulation complete')
