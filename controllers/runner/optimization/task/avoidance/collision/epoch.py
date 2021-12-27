from optimization.task.avoidance.Epoch import Epoch as Base
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.avoidance.collision.fitness import CollisionAvoidance
from robot.epuck import EPuck


class Epoch(Base):

    @staticmethod
    def objects(): return [f'box_{index}' for index in range(20)]


def new_epoch(robot: EPuck) -> Epoch:
    return new(robot, lambda epuck: Epoch(epuck, CollisionAvoidance))


def evolve_epoch(epoch: Epoch) -> Epoch:
    return evolve(epoch, lambda epuck: Epoch(epuck, CollisionAvoidance))
