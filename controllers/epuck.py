from controller import Robot
from enum import Enum
from functools import cache
from typing import Tuple


class Directions(Enum):
    """
    Robot motion-directions.
    They are represented as motor multipliers to achieve the directions
    """

    class Direction(Tuple):
        pass

    ahead: Direction = (1, 1)
    left: Direction = (-1, 1)
    right: Direction = (1, -1)


class EPuck(Robot):

    # robot wheels max speed
    MAX_SPEED = 6.28

    def run(self):
        """Execute a step and notify success"""

        return self.step(self.__time_step) != -1

    @cache
    def sensor(self, idx):
        """Return e-puck distance sensor idx"""

        return self.getDevice("ps" + str(idx))

    def distance(self, idx):
        """Get the distance value at the idx distance sensor"""

        return self.sensor(idx).getValue()

    def __init__(self):
        # get the time step of the current world
        super(Robot, self).__init__()
        self.__time_step = int(self.getBasicTimeStep())

        # get motors and initialize them
        self.leftMotor = self.getDevice('left wheel motor')
        self.rightMotor = self.getDevice('right wheel motor')
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        self.leftMotor.setVelocity(0.0)
        self.rightMotor.setVelocity(0.0)

        for i in range(8):
            self.sensor(i).enable(self.timestep)

    def move(self, direction: Directions.Direction):
        """Set the motors to move the robot in the specified direction"""

        leftSpeed, rightSpeed = map(lambda v: v * self.MAX_SPEED, direction)
        self.leftMotor.setVelocity(leftSpeed)
        self.rightMotor.setVelocity(rightSpeed)
