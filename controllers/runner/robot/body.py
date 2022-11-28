from controller import Supervisor
from robot.transducer.motor import Motor
from robot.transducer.transducer import Transducer
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

    __create_key = object()     # allows the constructor to be called only internally
    _instances = {}             # used to create a singleton class

    @classmethod
    def including(
            cls,
            sensors: Iterable[Transducer],
            motors: Iterable[Transducer] = tuple([Motor(f'{side} wheel motor') for side in ['left', 'right']])
    ):
        """
        Returns an EPuck instance with the given transducers.
        It should be the default way to get an EPuck instance.
        If it is called for the first time, create a new EPuck instance.
        If an EPuck instance already exists, set the new transducers and return it.
        """

        # create or update the instance
        if cls not in cls._instances:
            cls._instances[cls] = EPuck(cls.__create_key)
        else:
            cls._instances[cls].sensors = sensors
            cls._instances[cls].motors = motors

        # initialize sensors
        for sensor in sensors:
            sensor.initialize(cls._instances[cls])

        # initialize motors
        for motor in motors:
            motor.initialize(cls._instances[cls])

        return cls._instances[cls]

    def __init__(self, create_key):
        """Only internally callable constructor."""
        assert create_key == EPuck.__create_key, "Private constructor. Use `new` method to get an instance."
        Supervisor.__init__(self)
