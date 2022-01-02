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
import random

from itertools import product
from optimization.Simulation import Simulation
from optimization.task.Tasks import Tasks
from robot.epuck import EPuck

# set default constant seed for simulation
random.seed(1234)

# define the type of task to execute/achieve
task = Tasks.COLLISION_AVOIDANCE

# set if the world should have a dynamic behaviour (moving objects / obstacles)
task.value[0].dynamic = False

# minimum fitness needed to evolve a configuration instead of creating a new one
Simulation.MINIMUM_FITNESS = 30.0

# number of device instances that conform to a single datasheet
replica_count = 5

# number of epochs (net-connections) to test/simulate
epoch_count = 30

# number of steps for which the robot can run freely
epoch_duration = 300

# if true, continue simulation with best controller after the evolution finish
continue_after_evolution = False

# network density-configurations to tests (replicated 'replica_count' times)
densities = sorted(list(map(lambda _: _ + 5.0, range(5))) * replica_count)

# motor loads to test [1e3, 1e4, 1e5, 1e6]
loads = list(map(lambda exp: 10 ** exp, range(3, 7)))

# create the configurations and add a unique seed for each
settings = [(*_, random.randint(0, 9999)) for _ in product(densities, loads)]

# create the Robot instance
robot = EPuck(sensors=task.value[3])

print(
    '-' * 80 + '\n' +
    f'Running simulation of task `{task.name}`\n' +
    f'Tested densities: {sorted(set(densities))}\n' +
    f'Tested loads: [{", ".join(map("{:.0e}".format, loads))}]\n' +
    '-' * 80
)
