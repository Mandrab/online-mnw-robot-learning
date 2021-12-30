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

        # if the robot is in neutral zone, it cannot gain scores
        if floor_level == Colors.GRAY:
            return

        # if the target (black->white; white->black) has been reached (we
        # consider 3 color) increase fitness, otherwise decrease it
        if floor_level != self.initial_color:
            self.fitness += 2
        else:
            self.fitness -= 1

        self.counter += 1

    def value(self) -> float: return (self.fitness / self.counter + 1) / 0.03
