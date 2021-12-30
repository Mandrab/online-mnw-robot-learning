import random

from optimization.Epoch import Epoch as Base
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.tmaze.fitness import TMaze
from world.Colors import Colors
from robot.epuck import EPuck
from world.Manager import Manager

INITIAL_POSITION = [0, 3e-5, 0.4]
INITIAL_ROTATION = [0, -1, 0, 0]

BLACK_START = Colors.BLACK, [0, 2e-5, 0.25], [0, -1, 0.25]
WHITE_START = Colors.WHITE, [0, -1, 0.25], [0, 2e-5, 0.25]


class Epoch(Base):
    """An epoch designed to run the T-Maze task evolution."""

    # initialize some variables used during epoch run to restart controller
    duration = 200
    counter = 0

    def __init__(self, robot: EPuck):
        Base.__init__(self, robot, TMaze)

        # save the manager of the world
        self.world_manager = Manager(robot, 'evolvable')

    def step(self):
        """
        Run a step of the robot and collect its result/fitness in it.
        Periodically run the task again with random selected side to reach
        (defined by starting floor color)
        """

        if not self.counter % self.duration:

            # reset robot to start position
            self.world_manager.move('evolvable', INITIAL_POSITION)
            self.world_manager.rotate('evolvable', INITIAL_ROTATION)

            # ensure that changes take place
            self.world_manager.commit()

            # randomly set a floor as starting one (basically, hide the other)
            starting_color, black_position, white_position = BLACK_START
            if random.randint(0, 1):
                starting_color, black_position, white_position = WHITE_START
            self.world_manager.move('light_floor', white_position)
            self.world_manager.move('dark_floor', black_position)

            # (re)set initial color of evaluator utils
            self.evaluator.initial_color = starting_color

        # call super step
        Base.step(self)

        # increment counter
        self.counter += 1


def new_epoch(robot: EPuck) -> Epoch: return new(robot, Epoch)


def evolve_epoch(epoch: Epoch) -> Epoch: return evolve(epoch, Epoch)
