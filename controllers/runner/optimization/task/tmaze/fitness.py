from optimization.Fitness import Fitness
from .world import Colors


class TMaze(Fitness):
    """
    Calculate the fitness depending on the capability of reach the end of the
    maze and staying there as long as possible.
    """

    fitness: float = 0
    initial_color = Colors.NONE

    def reset(self):
        self.initial_color = Colors.NONE

    def update(self):
        floor_level = next(iter(self.robot.ground_sensors)).read()

        # map reading to discrete values (the comparison is in a neighborhood)
        if Colors.WHITE <= floor_level:
            floor_level = Colors.WHITE
        elif Colors.BLACK >= floor_level:
            floor_level = Colors.BLACK
        else:
            floor_level = Colors.GRAY

        # at the first step, save the initial ground color
        if Colors.NONE == self.initial_color:
            self.initial_color = floor_level

        # if the target has been reached (we consider 3 color), increase fitness
        if floor_level != self.initial_color and floor_level != Colors.GRAY:
            self.fitness += 1

    def value(self) -> float: return self.fitness
