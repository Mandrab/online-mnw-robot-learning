from optimization.fitness import Fitness as Base
from robot.component import grounds
from utils import adapt
from world.colors import Colors


class Fitness(Base):
    """
    Calculate the fitness depending on the capability of reach the end of the
    maze and staying there as long as possible. At each step the evaluator
    calculate fitness according to the following formula:
        2 * ~(f(i) or f(GRAY)) - 1 * f(i)
    where:
        - i in [BLACK, WHITE]: is the initial color of the floor.
        - f return [0, 1]: is a function that says if the robot is over the
          given floor. The return is 1 if it is on it, 0 otherwise.
        - ~: is a negate function.
    The formula gives a prize if the robot is not in the initial or gray floor
    and gives a penalty if it is in the initial one. The fitness are then
    averaged and the resulting range [-1, 2] is adapted to the range [0, 100].
    """

    initial_color = Colors.NONE

    fitness: float = 0.0
    counter: int = 0

    def update(self):
        # increment iteration counter
        self.counter += 1

        # get first ground-sensor reading
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

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return adapt(self.fitness / self.counter, (-1, 2), (0, 100))
