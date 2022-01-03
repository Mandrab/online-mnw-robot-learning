from .component import sensor, enable
from .conductor import Conductor
from controller import Supervisor
from .component.Motor import Motor
from typing import List
from utils import Frequency, adapt


class EPuck(Supervisor):
    """Represent the robot in the simulation"""

    # update/working time for robot modules
    run_frequency = Frequency(hz_value=10)

    # names of actuators (motors) actually used and their connection load
    motors = [Motor(f'{side} wheel motor') for side in ['left', 'right']]

    def __init__(self, sensors: List[str], conductor: Conductor = None):
        # get the time step of the current world
        Supervisor.__init__(self)

        # initialize (existing) sensors and keep 'successful' ones
        self.sensors = list(filter(enable(self), map(sensor, sensors)))

        # initialize motors
        for motor in self.motors:
            motor.robot = self

        # set the network controller
        self.conductor = conductor

    def run(self) -> bool:
        """Execute a step and notify possible success."""

        # webots has stopped/paused the simulation
        if self.step(self.run_frequency.ms) == -1:
            return False

        # get normalized sensors readings: [0, 1]
        stimulus = {s: s.read(normalize=True) for s in self.sensors}

        # run the controller
        outputs = self.conductor.evaluate(self.run_frequency.s, stimulus)

        # set the motors speed
        for motor, value in zip(self.motors, map(outputs.get, self.motors)):
            motor.speed = adapt(value, out_range=Motor.range(reverse=True))

        return True

    @property
    def motors_load(self) -> float: return self.conductor.load

    @motors_load.setter
    def motors_load(self, value: float): self.conductor.load = value
