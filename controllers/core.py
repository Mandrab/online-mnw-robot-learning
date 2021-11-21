import math

from controllers.conductor import Conductor
from epuck import EPuck
from nanowire_network_simulator import backup

################################################################################
# LOAD TESTED NETWORK

# load the memristive network
# it is created once and then exploited by the different robots
graph, datasheet, wires_dict = backup.read()

# todo find input & output node from tag/label

################################################################################
# SETUP SIMULATION

epoch_duration = 100    # in steps
delta_time = 0.2        # discrete evaluation time; in seconds

# crate robot controller
conductor = Conductor(graph, datasheet)
# todo add mapping

# create the Robot instance
robot = EPuck(conductor)

# get robot supervisor
supervisor = robot.getSupervisor()

# get measure function
# https://cyberbotics.com/doc/guide/supervisor-programming?tab-language=python
robot_node = supervisor.getFromDef("MY_ROBOT")
trans_field = robot_node.getField("translation")

# reset the simulation
supervisor.simulationReset()
supervisor.simulationSetMode(supervisor.SIMULATION_MODE_FAST)

# perform simulation steps until a epoch is completed
for _ in range(epoch_duration):
    robot.run(delta_time)

################################################################################
# EVALUATE RUN

# compute travelled distance
values = trans_field.getSFVec3f()
dist = math.sqrt(values[0] * values[0] + values[2] * values[2])

################################################################################
# RESULT SAVE

# todo
