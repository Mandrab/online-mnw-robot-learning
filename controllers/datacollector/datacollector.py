"""
This controller is aimed at collecting data for offline analysis of the
network's behaviour.
"""

import json
import os

from controller import Supervisor

TIME_STEP = 100  # ms; todo set equal to the epuck one used in other experiments
AVOID_FILE = 'avoid_obstacle_sensors_readings.dat'
DIRECT_FILE = 'direct_moving_sensors_readings.dat'

# delete save files if they already exists
if os.path.exists(AVOID_FILE):
    os.remove(AVOID_FILE)
if os.path.exists(DIRECT_FILE):
    os.remove(DIRECT_FILE)

# create the Robot instance.
robot = Supervisor()

# get the sensors devices
ps = [*map(robot.getDevice, [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
])]

# enable the sensors
for s in ps:
    s.enable(TIME_STEP)

# get motors devices
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')

# initialize to use with velocity values
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

# set initial speed
left_speed, right_speed = 6.28, 6.28

for _ in range(38):

    # execute a step of the simulation
    if robot.step(TIME_STEP) == -1:
        continue

    # check obstacles
    values = [ps[i].getValue() > 80 for i in [0, 1]]

    # check if it has to turn
    if any(values):
        left_speed, right_speed = -6.28, 6.28
    else:
        left_speed, right_speed = 6.28, 6.28

    # set velocities to the motors
    leftMotor.setVelocity(left_speed)
    rightMotor.setVelocity(right_speed)

    # save sensors readings to file
    with open(AVOID_FILE, "a") as file:
        file.write(json.dumps({i: s.getValue() for i, s in enumerate(ps)}))

# get handle to robot's translation field and change robot position
node = robot.getFromDef("robot")
trans_field = node.getField("translation")
trans_field.setSFVec3f([0, 0, 0.5])

# set motors speeds
leftMotor.setVelocity(6.28)
rightMotor.setVelocity(6.28)

# update sensors' readings
robot.step(TIME_STEP)

while ps[0].getValue() < 100:

    # execute a step of the simulation
    if robot.step(TIME_STEP) == -1:
        continue

    # save sensors readings to file
    with open(DIRECT_FILE, "a") as file:
        file.write(json.dumps({i: s.getValue() for i, s in enumerate(ps)}))
