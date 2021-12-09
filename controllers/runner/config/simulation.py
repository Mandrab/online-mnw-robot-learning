""" SIMULATION CONFIGURATIONS """
import random

from epuck import EPuck

# set constant seed for simulation
random.seed(1234)

# number of epochs (net-connections) to test/simulate
epoch_count = 20

# number of steps for which the robot can run freely
epoch_duration = 350

# network (density) configurations to tests
densities = [_ / 10.0 for _ in range(40, 201, 16)]

# create the Robot instance
robot = EPuck()
