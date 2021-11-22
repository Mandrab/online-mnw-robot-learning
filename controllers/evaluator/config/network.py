""" CONFIGURATION OF EXPERIMENT NETWORK """

import random

from nanowire_network_simulator import *
from nanowire_network_simulator import default as datasheet


# set constant seed for simulation
random.seed(1234)

################################################################################
# NETWORK LOAD OR SETUP

# if graph, datasheet and wires backup-files exist, import them
if all(backup.exist()):
    graph, datasheet, wires_dict = backup.read()

# if the backup-files does not exists, create the network and save it
else:
    # create a device that is represented by the given datasheet
    graph, wires_dict = minimum_viable_network(datasheet)

    # save a copy of the created graphs
    backup.save(datasheet, graph, wires_dict)

################################################################################
# INTERFACING

# select a random ground node
grounds = random_nodes(graph, avoid=set())

# select source nodes from non-grounds nodes
sources = random_nodes(graph, grounds, count=4)

# select output nodes from non-grounds & non-source nodes # todo distance
loads = random_loads(graph, grounds | sources, count=2)

# todo labelize graph (i/o) and save
# backup.save(default, graph, wires_dict)

# todo find input & output node from tag/label
