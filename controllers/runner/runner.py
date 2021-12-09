import time

from config.simulation import *
from optimization.utils import import_simulations, new_simulations, save_epoch

SAVING_FOLDER = '../../res/configuration/'

################################################################################
# SIMULATION SETUP

# import simulations from the 'controllers' folder
simulations = import_simulations(robot)

# if no simulations have been imported, generate new ones
if not simulations:
    simulations = new_simulations(robot, densities)

################################################################################
# SIMULATION EXECUTION

# create a list to collect the best epoch for each simulation
best_epochs = []

# run simulations of different devices
for simulation in simulations:
    g, d = simulation.controller.network, simulation.controller.datasheet
    print(
        'Effective network density:',
        g.number_of_nodes() * d.mean_length * d.mean_length / (d.Lx * d.Ly),
        'wires:', g.number_of_nodes()
    )

    # initialize the first epoch/run of the simulation
    simulation.initialize(epoch_duration)

    # simulate count-epochs run
    for epoch in range(epoch_count):
        simulation.simulate(epoch_duration)

    # save the best found epoch/configuration
    best_epochs += [simulation.best_epoch]

################################################################################
# RESULT SAVING

# save the configurations in a file
for index, epoch in enumerate(best_epochs):
    file_format = SAVING_FOLDER + '{name}' + f'.{time.time()}.{index}.dat'
    save_epoch(epoch, file_format)

################################################################################
# BEST CONTROLLER RUN

print('Running the best scoring controller')
robot.simulationReset()

# get the best configuration overall
best = max(best_epochs, key=lambda e: e.fitness.value())

# run the best controller until it is stopped
robot.conductor = best.controller
while robot.run():
    pass
