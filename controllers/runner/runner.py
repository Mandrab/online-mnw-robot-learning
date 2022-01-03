import os

from config.simulation import *
from datetime import datetime
from optimization.utils import import_simulations, new_simulations, save_epoch

CONFIGURATIONS_LOCATION = '../../res/configuration'
SAVING_FOLDER = datetime.today().strftime('%Y-%m-%d.%H%M%S%f')


################################################################################
# SIMULATION SETUP

# import simulations from the 'controllers' folder
simulations = import_simulations(robot, task_type=task)

# if no simulations have been imported, generate new ones
if not simulations:
    simulations = new_simulations(robot, settings, task_type=task)

################################################################################
# SIMULATION EXECUTION

# create a list to collect the best epoch for each simulation
best_epochs = []

# run simulations of different devices
for simulation in simulations:
    print(simulation)

    # initialize the first epoch/run of the simulation
    simulation.initialize()

    # simulate count-epochs run
    for epoch in range(epoch_count):
        simulation.simulate(epoch_duration)

    # save the best found epoch/configuration
    best_epochs += [simulation.best_epoch]

################################################################################
# RESULT SAVING

# create saving folder
path = os.path.join(CONFIGURATIONS_LOCATION, SAVING_FOLDER)
os.mkdir(path)

# save the configurations in a file
for index, epoch in enumerate(best_epochs):
    file_format = str(path) + '/{name}' + f'.{index}.dat'
    save_epoch(epoch, file_format)

################################################################################
# BEST CONTROLLER RUN OR EXIT

if not continue_after_evolution:
    # exit the simulator
    print('Simulation complete')
    robot.simulationQuit(0)

print('Running the best scoring controller')
robot.simulationReset()

# get the best configuration overall
best = max(best_epochs, key=lambda e: e.evaluator.value())

# run the best controller until it is stopped; use the step function to allow
# more advanced processing of the environment by the epoch; since thats the
# last operation, the update of the fitness function is not considered a problem
robot.conductor = best.controller
while True:
    best.step()
