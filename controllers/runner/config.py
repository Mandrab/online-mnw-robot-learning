"""
This file define the characteristic of the evolution strategies chosen.
The required process is the following:

    1-  for each 'density' in 'densities', 'replica_count' devices are created
        with different 'seeds'. This allow same densities with different network
        topology and allows for statistical evaluations
    2-  the connections to each device are evolved 'epoch_count' times.
    3-  each device-connections configuration runs 'epoch_duration' times, and
        in this time is evaluated

               -- seed -- device --[evolution path 1]-- best connection, fitness
             /
    Density 1 --- seed -- device --[evolution path 2]-- best connection, fitness
             \
               -- seed -- device --[evolution path N]-- best connection, fitness

               -- seed -- device --[evolution path 1]-- best connection, fitness
             /
    Density 2 --- seed -- device --[evolution path 2]-- best connection, fitness
             \
               -- seed -- device --[evolution path N]-- best connection, fitness
"""
import logging
import os
import random

from datetime import datetime
from itertools import product
from logger import logger, Settings, setup
from nanowire_network_simulator import LOGGER_NAME as NNS_LOGGER_NAME
from optimization.task import Tasks, Task
from robot.body import EPuck

################################################################################
# SIMULATION CONFIGURATIONS

# set default constant seed for simulation setup
random.seed(1234)

# define the type of task to execute/achieve
task: Tasks = Tasks.COLLISION_AVOIDANCE
task_name: str = task.name
task: Task = task.value

# set if the world should have a dynamic behaviour (moving objects / obstacles)
task.life_manager.dynamic = False

# number of device instances that conform to a single datasheet
replica_count = 30

# number of epochs (net-connections) to test/simulate
epoch_count = 30

# number of steps for which the robot can run freely
epoch_duration = 200

# network density-configurations to tests (replicated 'replica_count' times)
densities = sorted(list(map(lambda _: _ * 2.5 + 5.0, range(3))) * replica_count)

# motor loads to test [1e3, 1e4, 1e5, 1e6]
loads = list(map(lambda exp: 10 ** exp, range(3, 7)))

# create the configurations and add a unique seed for each
settings = [(*_, random.randint(0, 9999)) for _ in product(densities, loads)]

# define a tuple that contains the information used to simulate
simulation_settings = task, epoch_count, epoch_duration

# create the Robot instance
robot = EPuck(sensors=task.sensors)

################################################################################
# DATA SAVE SETUP

# create the folder for saving the simulation files
CONFIGURATIONS_LOCATION = '../../res/configuration'
SAVING_FOLDER = datetime.today().strftime('%Y-%m-%d.%H%M%S%f')
os.mkdir(save_path := os.path.join(CONFIGURATIONS_LOCATION, SAVING_FOLDER))

setup(logger, Settings(path=save_path + '/', plot_mode=Settings.Mode.NONE))
setup(logging.getLogger(NNS_LOGGER_NAME), Settings(path=save_path + '/'))
logger.info(
    '-' * 47 + '\n' +
    f'Running simulation of task `{task_name}`\n' +
    f'Tested densities: {sorted(set(densities))}\n' +
    f'Tested loads: [{", ".join(map("{:.0e}".format, loads))}]\n' +
    '-' * 80
)
