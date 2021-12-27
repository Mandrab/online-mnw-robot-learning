from abc import abstractmethod
from collections import Callable
from optimization.Epoch import Epoch as Base
from optimization.Fitness import Fitness
from random import random
from robot.epuck import EPuck
from world.Manager import Manager


class Epoch(Base):

    delta = [[0, 0, 0] for _ in range(6)]
    multiplier = 0.005

    dynamic = False
    update_time = 100
    counter = 0

    def __init__(self, robot: EPuck, evaluator: Callable[[EPuck], Fitness]):
        Base.__init__(self, robot, evaluator)

        # save the manager of the world
        self.world_manager = Manager(robot, 'evolvable')

    @staticmethod
    @abstractmethod
    def objects():
        """Returns the name of the moving objects."""
        NotImplemented('Shall return the name of the moving objects.')

    @staticmethod
    def force_in_arena(coordinate: float):
        """Returns the coordinate limited into the arena."""
        return min(max(coordinate, -0.5), 0.5)

    def step(self):

        # get object position and update them
        positions = map(self.world_manager.position, self.objects())
        positions = filter(None, positions)

        # update object directions
        if not self.counter % self.update_time:
            self.delta = [[random() - 0.5, 0, random() - 0.5] for _ in range(6)]
            self.delta = [[_ * self.multiplier for _ in p] for p in self.delta]

        if self.dynamic:
            for a, p, d in zip(self.objects(), positions, self.delta):
                new_p = [*map(self.force_in_arena, map(sum, zip(p, d)))]
                self.world_manager.move(a, new_p)
            self.world_manager.commit(ensure=True)

        # call super step
        Base.step(self)

        # increment counter
        self.counter += 1
