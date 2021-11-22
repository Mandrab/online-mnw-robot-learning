from conductor import Conductor
from controller import Robot
from enum import Enum


class Sensor(Enum):
    """
    Map the sensor angle to its string name.
    The angle is clock wise from the front of the robot.
    """
    A25 = 'ps0'     # ~front
    A45 = 'ps1'     # front right
    A90 = 'ps2'     # right
    A155 = 'ps3'    # back right
    A205 = 'ps4'    # back left
    A270 = 'ps5'    # left
    A315 = 'ps6'    # front left
    A335 = 'ps7'    # ~front


__sensors = [s.value for s in Sensor]


class EPuck(Robot):

    # robot wheels max speed
    MAX_SPEED = 6.28

    def __init__(self, conductor: Conductor):
        # get the time step of the current world
        super(Robot, self).__init__()

        # get left motors and initialize it
        self.leftMotor = self.getDevice('left wheel motor')
        self.leftMotor.setPosition(float('inf'))
        self.leftMotor.setVelocity(0.0)

        # get right motors and initialize it
        self.rightMotor = self.getDevice('right wheel motor')
        self.rightMotor.setPosition(float('inf'))
        self.rightMotor.setVelocity(0.0)

        # enable the distance sensors
        for i in range(8): self.sensor(i).enable(self.timestep)

        # set the network controller
        self.conductor = conductor

    def run(self, delta_time: float):
        """Execute a step and notify success"""

        # webots has stopped/paused the simulation
        if self.step(delta_time) == -1:
            return False

        # get sensors readings
        stimulus = dict((s, self.getDevice(s).getValue()) for s in __sensors)

        # run the controller
        outputs = self.conductor.evaluate(delta_time, stimulus)

        # todo remap to range stimulus and outputs ?

        # set the outputs
        self.leftMotor.setVelocity(outputs['left wheel motor'])
        self.rightMotor.setVelocity(outputs['right wheel motor'])

        return True
