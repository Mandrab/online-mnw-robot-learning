import math

from conductor import Conductor
from config.simulation import *
from config.network import *
from epuck import EPuck

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
