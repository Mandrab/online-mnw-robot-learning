import math

from optimization.fitness import Fitness as Base


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities"""

    fitness: float = 0
    counter: int = 0

    def update(self):
        # get the proximity measures in range 0-1
        proximity = [s.normalized_value for s in self.robot.sensors]
        # print(proximity)
        # print(list(map(lambda x: math.log(1 - x, 2), proximity)))
        # proximity = list(map(lambda x: abs(math.log(1 - x, 2)), proximity))

        # calculate the distance measure,
        # setting it to 0 if there is no proximal obstacle.
        # this avoids that no readings are considered in range
        distances = [0.0 if d < .05 else 1 - d for d in proximity]

        # calculate the average distance
        self.fitness += sum(distances) / len(self.robot.sensors)
        self.counter += 1

    def value(self) -> float:
        if self.counter == 0:
            return 0.0
        return 100 * self.fitness / self.counter
