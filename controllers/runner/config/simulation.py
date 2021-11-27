""" SIMULATION CONFIGS """
import itertools
import random

from epuck import EPuck

# set constant seed for simulation
random.seed(1234)

epoch_count = 50       # number of epochs (robot) to run in the simulation
epoch_duration = 100    # in steps; an epoch allow a robot to run freely

# grid-search like: get the cross-product of the given parameters
grid = [*itertools.product(*[
    # wires count, device size and wire length
    [(200, 100, 20)],
    # [(300, 200, 40), (500, 200, 30), (800, 200, 20)],
    # # ranges
    [(True, (-10.0, 0))]
    # itertools.product(*[
    #     # sensors range is raw -> (0, 4095) / (0, 7)
    #     [True, False],
    #     # network range
    #     [(-10.0, 10.0), (0.0, 10.0)]
    # ])
])]

# create the Robot instance
robot = EPuck()
