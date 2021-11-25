import math

from conductor import Conductor
from config.simulation import *
from config.network import *
from epuck import EPuck

################################################################################
# ROBOT SETUP

# crate robot controller
conductor = Conductor(graph, datasheet)

# create the Robot instance
robot = EPuck(conductor)

# randomly connect the actuators(motors) to the network
output_nodes = random_nodes(conductor.network, avoid=set(), count=2)
mapping = dict(zip(robot.motors, output_nodes))
conductor.set_actuators(robot.motors, mapping)

# get nodes distant 2 step from outputs nodes
source_selector = minimum_distance_selection([*output_nodes], distance=2)
viable_nodes = [*source_selector(conductor.network, [], -1)]

# randomly select input nodes between the ones that are suitable for the
# selection
# the selected nodes may be repeated
input_nodes = [
    viable_nodes[random.randrange(len(viable_nodes))] for _ in robot.sensors
]
mapping = dict(zip(robot.sensors, input_nodes))
conductor.set_sensors(robot.sensors, mapping)

# initialize the network with the given setting
conductor.initialize()

################################################################################
# DEFINE SIMULATIONS UTILITIES

# get measure function
# https://cyberbotics.com/doc/guide/supervisor-programming?tab-language=python
node = robot.getFromDef('evolvable')
trans_field = node.getField('translation')

# reset the simulation
robot.simulationReset()
robot.simulationSetMode(robot.SIMULATION_MODE_FAST)

################################################################################
# RUN THE SIMULATION

# simulate count epochs run
for epoch in range(epoch_count):

    print(f'Start of {epoch} simulation')
    # perform simulation steps until a epoch is completed
    for _ in range(epoch_duration):

        # run a simulation step
        robot.run()

    # randomly connect the sensors to the network
    input_nodes = mutate(
        graph=conductor.network,
        sources=input_nodes,
        ground=-1,
        probability=0.3,
        minimum_mutants=1,
        maximum_mutants=4,
        viable_node_selection=source_selector
    )

    mapping = dict(zip(robot.sensors, input_nodes))
    conductor.set_sensors(robot.sensors, mapping)

################################################################################
# EVALUATE RUN

# compute travelled distance
values = trans_field.getSFVec3f()
dist = math.sqrt(values[0] * values[0] + values[2] * values[2])

################################################################################
# RESULT SAVE

# todo
