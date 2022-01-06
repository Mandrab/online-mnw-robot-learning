from controller import Supervisor
from robot.component import sensor, enable
from robot.component.motor import Motor
from utils import Frequency
from typing import Iterable


class EPuck(Supervisor):
    """
    Represents the body of the robot in the simulation. It includes a reference
    to the sensors and actuators and act as a mediator to improve code quality.
    It also includes some additional information specific to webots like the
    update frequency of the controller.
    """

    # update/working time for robot modules
    run_frequency = Frequency(hz_value=10)

    # names of actuators (motors) actually used and their connection load
    motors = tuple([Motor(f'{side} wheel motor') for side in ['left', 'right']])

    def __init__(self, sensors: Iterable[str]):
        Supervisor.__init__(self)

        # initialize (existing) sensors and keep 'successful' ones
        self.sensors = tuple(filter(enable(self), map(sensor, sensors)))

        # initialize motors
        for motor in self.motors:
            motor.robot = self
