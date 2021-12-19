from optimization.Epoch import Epoch as Base
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.avoidance.fitness import CollisionAvoidance
from robot.epuck import EPuck
from typing import List


class Epoch(Base):
    """An epoch designed to run the collision-avoidance task evolution."""

    def __init__(self, robot: EPuck, sensors: List[int], actuators: List[int]):
        Base.__init__(self, robot, sensors, actuators, CollisionAvoidance)


def new_epoch(robot: EPuck) -> Epoch: return new(robot, Epoch)


def evolve_epoch(epoch: Epoch) -> Epoch: return evolve(epoch, Epoch)
