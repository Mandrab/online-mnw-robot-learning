from conductor import Conductor
from controller import Supervisor


class EPuck(Supervisor):
    """Represent the robot in the simulation"""

    # specify update time for robot modules (in ms)
    run_frequency = 100

    # names of the sensors and actuators actually used
    sensors = [f'ps{idx}' for idx in [0, 2, 5, 7]]
    motors = [f'{side} wheel motor' for side in ['left', 'right']]

    def __init__(self, conductor: Conductor):
        # get the time step of the current world
        super().__init__()

        # initialize distance sensors
        for key in self.sensors:
            self.getDevice(key).enable(self.run_frequency)

        # set the network controller
        self.conductor = conductor

    def run(self):
        """Execute a step and notify success"""

        # webots has stopped/paused the simulation
        if self.step(self.run_frequency) == -1:
            return False

        # get sensors readings
        stimulus = {k: self.read(k) for k in self.sensors}

        # run the controller
        outputs = self.conductor.evaluate(
            update_time=self.run_frequency,
            stimulus=stimulus,
            actuators_resistance=100
        )

        # set the motors
        self.move(*map(outputs.get, self.motors))

        return True

    def move(self, left_speed: float, right_speed: float):
        for key, value in zip(self.motors, [left_speed, right_speed]):
            device = self.getDevice(key)
            device.setPosition(float('inf'))
            device.setVelocity(value)

    def read(self, key) -> float:
        return self.getDevice(key).getValue()
