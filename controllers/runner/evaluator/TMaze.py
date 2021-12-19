from .Fitness import Fitness

# if the robot get far from the end of the maze its score must decrease by a
# multiplicative factor at each step
DECAY = 0.95

# definition of simulation colors
NONE = -1
WHITE = 600
GRAY = 400
BLACK = 300
DELTA_COLOR = 50


class TMaze(Fitness):
    """
    Calculate the fitness depending on the capability of reach the end of the
    maze.
    """

    __fitness: float = 0
    __initial_color = NONE

    def update(self):
        floor_level = next(iter(self.robot.ground_sensors)).read()

        # at the first step, save the initial ground color
        if self.__initial_color == NONE:
            self.__initial_color = WHITE if equal(floor_level, WHITE) else BLACK

        if (
                not equal(floor_level, self.__initial_color)
                and
                not equal(floor_level, GRAY)
        ):
            self.__fitness += 1
        else:
            self.__fitness *= DECAY

    def value(self) -> float: return self.__fitness


def equal(a, b, delta=DELTA_COLOR): return b - delta < a < b + delta
