from component import Sensor, Motor
from conductor import Conductor
from controller import Supervisor
from ..utils import Frequency


class EPuck(Supervisor):
    """Represent the robot in the simulation"""

    # update/working time for robot modules
    run_frequency = Frequency(hz_value=10)

    # names of the sensors and actuators actually used
    sensors = [Sensor(f'ps{idx}') for idx in range(8)]
    motors = [Motor(f'{side} wheel motor') for side in ['left', 'right']]

    def __init__(self, conductor: Conductor = None):
        # get the time step of the current world
        super().__init__()

        # initialize distance sensors
        for sensor in self.sensors:
            sensor.robot = self
            sensor.enable(self.run_frequency.ms)

        # initialize motors
        for motor in self.motors:
            motor.robot = self

        # set actuators and motors range
        self.sensors_range = next(iter(self.sensors)).range
        self.motors_range = next(iter(self.motors)).range

        # set the network controller
        self.conductor = conductor

    def run(self, raw_signal: bool = True):
        """Execute a step and notify success"""

        # webots has stopped/paused the simulation
        if self.step(self.run_frequency.ms) == -1:
            return False

        # get sensors readings
        stimulus = {s: s.read(raw_signal) for s in self.sensors}

        # run the controller
        outputs = self.conductor.evaluate(
            update_time=self.run_frequency.s,
            inputs=stimulus,
            inputs_range=self.sensors_range(raw_signal),
            outputs_range=self.motors_range(raw_signal),
            actuators_load=1e6  # MOhm
        )

        # set the motors speed
        for motor, value in zip(self.motors, map(outputs.get, self.motors)):
            motor.speed = value

        return True
