from optimization.Epoch import Epoch
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.run.fitness import Distance
from robot.epuck import EPuck


def new_epoch(robot: EPuck) -> Epoch:
    return new(robot, lambda epuck: Epoch(epuck, Distance))


def evolve_epoch(epoch: Epoch) -> Epoch:
    return evolve(epoch, lambda epuck: Epoch(epuck, Distance))
