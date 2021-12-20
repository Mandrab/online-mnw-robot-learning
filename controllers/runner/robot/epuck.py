from .component import IRSensor, Motor, GroundSensor
from .conductor import Conductor
from controller import Supervisor
from itertools import chain
from utils import Frequency


class EPuck(Supervisor):
    """Represent the robot in the simulation"""

    # update/working time for robot modules
    run_frequency = Frequency(hz_value=10)

    # names of the sensors and actuators actually used
    ir_sensors = [IRSensor(f'ps{idx}') for idx in range(8)]
    ground_sensors = [GroundSensor('gs0')]
    motors = [Motor(f'{side} wheel motor') for side in ['left', 'right']]

    def __init__(self, conductor: Conductor = None):
        # get the time step of the current world
        super().__init__()

        # set actuators and motors range
        self.ir_sensors_range = next(iter(self.ir_sensors)).range
        self.ground_sensors_range = next(iter(self.ground_sensors)).range
        self.motors_range = next(iter(self.motors)).range

        # initialize distance sensors
        for sensor in chain(self.ir_sensors, self.ground_sensors):
            sensor.robot = self
            if isinstance(sensor, GroundSensor) and not sensor.exists():
                self.ground_sensors.remove(sensor)
            else:
                sensor.enable(self.run_frequency.ms)

        # initialize motors
        for motor in self.motors:
            motor.robot = self

        # set the network controller
        self.conductor = conductor

    def run(self, raw_signal: bool = True):
        """Execute a step and notify success"""

        # webots has stopped/paused the simulation
        if self.step(self.run_frequency.ms) == -1:
            return False

        # get sensors readings
        stimulus = {s: s.read(raw_signal) for s in self.ir_sensors}

        # run the controller ; todo add ground sensor usage for tmaze task
        outputs = self.conductor.evaluate(
            update_time=self.run_frequency.s,
            inputs=stimulus,
            inputs_range=self.ir_sensors_range(raw_signal),
            outputs_range=self.motors_range(raw_signal),
            actuators_load=1e6  # MOhm
        )

        # set the motors speed
        for motor, value in zip(self.motors, map(outputs.get, self.motors)):
            motor.speed = value

        return True
