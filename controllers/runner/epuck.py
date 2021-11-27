from component import Sensor, Motor
from conductor import Conductor
from controller import Supervisor


class EPuck(Supervisor):
    """Represent the robot in the simulation"""

    # specify update time for robot modules (in ms)
    run_frequency: int = 100

    # names of the sensors and actuators actually used
    sensors = [Sensor(f'ps{idx}') for idx in [0, 2, 5, 7]]
    motors = [Motor(f'{side} wheel motor') for side in ['left', 'right']]

    def __init__(self, conductor: Conductor):
        # get the time step of the current world
        super().__init__()

        # initialize distance sensors
        for sensor in self.sensors:
            sensor.robot = self
            sensor.enable(self.run_frequency)

        # initialize motors
        for motor in self.motors:
            motor.robot = self

        # set the network controller
        self.conductor = conductor

    def run(self):
        """Execute a step and notify success"""

        # webots has stopped/paused the simulation
        if self.step(self.run_frequency) == -1:
            return False

        # get sensors readings todo
        stimulus = {sensor: sensor.read() for sensor in self.sensors}
        print('distances:\t', stimulus)

        # run the controller
        outputs = self.conductor.evaluate(
            update_time=self.run_frequency,
            stimulus=stimulus,
            stimulus_range=self.sensors[0].range(),
            outputs_range=self.motors[0].range(),
            actuators_resistance=100
        )
        # print('motors:\t\t', outputs)

        # set the motors speed
        for motor, value in zip(self.motors, map(outputs.get, self.motors)):
            motor.speed = value

        return True
