from conductor import Conductor
from controller import Supervisor
from controllers.evaluator.components import motors, sensors


class EPuck(Supervisor):
    # robot wheels max speed
    MAX_SPEED = 6.28

    # specify update time for robot modules (in ms)
    run_frequency = 100

    def __init__(self, conductor: Conductor):
        # get the time step of the current world
        super().__init__()

        # initialize left and right motors
        for _, motor in motors.items():
            motor.robot = self

        # initialize distance sensors
        for _, sensor in sensors.items():
            sensor.init(self, self.run_frequency)

        # set the network controller
        self.conductor = conductor

    def run(self):
        """Execute a step and notify success"""

        # webots has stopped/paused the simulation
        if self.step(self.run_frequency) == -1:
            return False

        # get sensors readings
        stimulus = dict([(v, v.read) for _, v in sensors.items()])

        # run the controller
        outputs = self.conductor.evaluate(self.run_frequency, stimulus)

        # todo remap to range stimulus and outputs ?

        # set the outputs
        motors['LEFT'].speed = outputs[motors['LEFT']]
        motors['RIGHT'].speed = outputs[motors['RIGHT']]

        return True
