from conductor import adapt  # todo move to utils file
from epuck import EPuck
from functools import reduce
from math import sqrt
from operator import add, sub


class Fitness:
    """Calculate the fitness achieved during a epoch"""

    __fitness: float = 0
    __counter: int = 0

    def __init__(self, robot: EPuck):
        # save robot instance
        self.robot = robot

    def fitness(self) -> float:
        return 100 * self.__fitness / self.__counter

    def update(self):
        # get the most near measure and make it in range 0-1
        value = max(sensor.read() for sensor in self.robot.sensors)

        min_value = self.robot.sensors[0].lower_bound()
        max_value = self.robot.sensors[0].upper_bound()

        # get motors velocities and make them in range 0-1
        speeds = [motor.speed for motor in self.robot.motors]
        speeds = [adapt(value, (-6.14, 6.14), (0.0, 1.0)) for value in speeds]

        max_proximity = adapt(value, (min_value, max_value), (0, 1))
        average_speed = sum(speeds) / 2.0
        directions = sqrt(abs(reduce(sub, speeds)))

        self.__fitness += (1 - max_proximity) * (1 - directions) * average_speed
        self.__counter += 1


class Distance:
    """Calculate the distance travelled by the robot"""

    # travelled distance
    distance: float = 0

    def __init__(self, robot: EPuck):
        # save robot instance
        self.robot = robot

        # get measure function
        # https://cyberbotics.com/doc/guide/supervisor-programming?tab-language=python
        node = robot.getFromDef('evolvable')
        self.translation = node.getField('translation')

        # get position of the robot at the step (x, y, z)
        self.position = self.translation.getSFVec3f()[:2]

    def update(self):
        """To be called after each movement"""

        # get position of the robot at the step (x, y, z)
        new_position = self.translation.getSFVec3f()[:2]

        # update distance adding travelled distance (euclidean)
        points = zip(self.position, new_position)
        self.distance += sqrt(reduce(add, [pow(x - y, 2) for x, y in points]))

        # update position
        self.position = new_position
