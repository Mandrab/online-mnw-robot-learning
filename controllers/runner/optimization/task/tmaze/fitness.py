from operator import sub
from optimization.Fitness import Fitness
from robot.component import grounds
from world.Colors import Colors


class TMaze(Fitness):
    """
    Calculate the fitness depending on the capability of reach the end of the
    maze and staying there as long as possible.
    """

    fitness: float = 0.0
    counter: float = 0.0
    initial_color = Colors.NONE

    def update(self):
        floor_level = next(iter(grounds(self.robot.sensors))).read()

        # map reading to discrete values
        floor_level = Colors.convert(floor_level)

        # if the target has been reached (we consider 3 color), increase fitness
        if floor_level != self.initial_color and floor_level != Colors.GRAY:
            self.fitness += 1

        # calculate robot direction as left < 0, right > 0
        robot_direction = sub(*map(lambda _: _.speed, self.robot.motors)) / 12.0

        # if robot is moving toward target, increase fitness
        if self.initial_color == Colors.BLACK:
            self.fitness += robot_direction
        elif self.initial_color == Colors.WHITE:
            self.fitness -= robot_direction

        self.counter += 1

    def value(self) -> float: return 50 * self.fitness / self.counter
