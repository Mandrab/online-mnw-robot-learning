""" SIMULATION CONFIGURATIONS """
import random

from epuck import EPuck

# set constant seed for simulation
random.seed(1234)

# number of epochs (net-connections) to test/simulate
epoch_count = 20

# number of steps for which the robot can run freely
epoch_duration = 150

# network configurations to tests
# syntax: (wires count, device size, wire length)
grid = [
    (100, 45, 10),      # density 4.94
    (100, 40, 9),       # density 5.06
    (100, 35, 8),       # density 5.22
    (250, 40, 6),       # density 5.63
    (400, 50, 6),       # density 5.76
    (400, 80, 10)       # density 6.25
]

# create the Robot instance
robot = EPuck()
