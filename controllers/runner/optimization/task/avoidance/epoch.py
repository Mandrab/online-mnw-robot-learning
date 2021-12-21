from optimization.Epoch import Epoch
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.avoidance.fitness import CollisionAvoidance as Evaluator
from robot.epuck import EPuck


def new_epoch(robot: EPuck) -> Epoch:
    return new(robot, lambda epuck: Epoch(epuck, Evaluator))


def evolve_epoch(epoch: Epoch) -> Epoch:
    return evolve(epoch, lambda epuck: Epoch(epuck, Evaluator))
