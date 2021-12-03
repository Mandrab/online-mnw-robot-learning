"""
This is a controller that uses the motor-schema approach, based on the potential
fields. The direction and speed is calculated as a sum of potential vectors.
"""

from controller import Robot
from functools import reduce
from math import radians, sin
from controllers.motorschema.utils import adapt, polar_vector_sum

TIME_STEP = 100  # ms; todo set equal to e-puck one used in other experiments

# create the Robot instance.
robot = Robot()

# get the sensors devices
ps = [*zip(map(robot.getDevice, [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
]), map(radians, [
    -15, -45, -90, -150,
    150, 90, 45, 15,
    # 210, 270, 315, 330
]))]

# enable the sensors
for s, _ in ps:
    s.enable(TIME_STEP)

# get motors devices
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')

# initialize to use with velocity values
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

while robot.step(TIME_STEP) != -1:

    # define the vectors (intensity & angle) list
    vectors = [(adapt(s.getValue(), (65, 1550), (1, 0)), a) for s, a in ps]
    vectors = [(length * abs(sin(angle)), angle) for length, angle in vectors]

    # sum vectors
    length, angle = reduce(polar_vector_sum, vectors)

    # calculate speeds
    left_speed = length - angle * 5.2 / 2
    right_speed = length + angle * 5.2 / 2

    # set velocities to the motors
    leftMotor.setVelocity(left_speed)
    rightMotor.setVelocity(right_speed)
