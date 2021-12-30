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

# network density-configurations to tests and generating seeds
densities = {
    _ + 5: [random.randint(0, 9999) for _ in range(replica_count)]
    for _ in range(5)
}

# create the Robot instance
robot = EPuck(sensors=task.value[3])
robot.motors_load = 1e6
