from operator import sub
from optimization.Fitness import Fitness
from robot.component import grounds
from .world import Colors


class TMaze(Fitness):
    """
    Calculate the fitness depending on the capability of reach the end of the
    maze and staying there as long as possible.
    """

    fitness: float = 0.0
    initial_color = Colors.NONE

    def update(self):
        floor_level = next(iter(grounds(self.robot.sensors))).read()

        # map reading to discrete values (the comparison is in a neighborhood)
        if Colors.WHITE <= floor_level:
            floor_level = Colors.WHITE
        elif Colors.BLACK >= floor_level:
            floor_level = Colors.BLACK
        else:
            floor_level = Colors.GRAY

        # if the target has been reached (we consider 3 color), increase fitness
        if floor_level != self.initial_color and floor_level != Colors.GRAY:
            self.fitness += 1

        # calculate robot direction as left < 0, right > 0
        robot_direction = sub(*map(lambda _: _.speed, self.robot.motors))

        # if robot is moving toward target, increase fitness
        if self.initial_color == Colors.BLACK:
            self.fitness += robot_direction
        elif self.initial_color == Colors.WHITE:
            self.fitness -= robot_direction

    def value(self) -> float: return self.fitness
