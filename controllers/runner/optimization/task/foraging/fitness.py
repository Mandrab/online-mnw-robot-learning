from optimization.task.avoidance.collision import Fitness as Base
from robot.transducer import grounds
from robot.transducer.motor import Motor
from utils import adapt
from world.colors import Colors


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities together with the foraging behavior."""

    def update(self):

        # calculate the collision avoidance fitness
        Base.update(self)

        # get first ground-sensor reading and map to discrete values
        floor_level = Colors.convert(next(iter(grounds(self.robot.sensors))).value)

        # get the gripper actuator
        actuator = next(filter(lambda _: _ is not Motor, self.robot.motors))

        # check if the robot just picked up an object in the black region
        if actuator.captured and floor_level == Colors.BLACK:
            self.fitness += 50

        # check if the robot deposited an object in the white region
        if actuator.deposited and floor_level == Colors.WHITE:
            self.fitness += 50

        # give a penalty if the robot deposited the object in a region different from the white one
        if actuator.deposited and floor_level != Colors.WHITE:
            self.fitness -= 100

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return adapt(self.fitness / self.counter, (-100, 51), (0, 100))
