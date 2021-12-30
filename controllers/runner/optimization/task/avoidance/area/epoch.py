from optimization.task.avoidance.Epoch import Epoch as Base
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.avoidance.area.fitness import AreaAvoidance
from robot.epuck import EPuck


class Epoch(Base):

    @staticmethod
    def objects(): return [f'area_{index}' for index in range(15)]

    @staticmethod
    def force_in_arena(coordinate: float):
        return min(max(coordinate, -2.5), 2.5)


def new_epoch(robot: EPuck) -> Epoch:
    return new(robot, lambda epuck: Epoch(epuck, AreaAvoidance))


def evolve_epoch(epoch: Epoch) -> Epoch:
    return evolve(epoch, lambda epuck: Epoch(epuck, AreaAvoidance))
