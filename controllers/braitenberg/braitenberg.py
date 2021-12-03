"""
This is a Braitenberg-like controller. It differs from a classical one in that
it evaluates also side sensors and it weight them according to their importance.
"""

from controller import Robot
from controllers.braitenberg.utils import adapt

TIME_STEP = 100  # ms; todo set equal to the epuck one used in other experiments

# create the Robot instance.
robot = Robot()

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

while robot.step(TIME_STEP) != -1:
    # get values in 65, 1550
    fl = sum(ps[i].getValue() * w for i, w in zip([0, 1, 2], [1.0, 0.7, 0.4]))
    fr = sum(ps[i].getValue() * w for i, w in zip([7, 6, 5], [1.0, 0.7, 0.4]))

    # make values in -6.28, 6.28
    l = adapt(fl, (65, 1550), (6.28, -6.28))
    r = adapt(fr, (65, 1550), (6.28, -6.28))

    # set velocities to the motors
    leftMotor.setVelocity(l)
    rightMotor.setVelocity(r)
