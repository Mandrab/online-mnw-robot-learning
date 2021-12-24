import random

from optimization.Epoch import Epoch as Base
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.tmaze.fitness import TMaze
from world import Colors
from robot.epuck import EPuck

INITIAL_POSITION = [0, 3e-5, 0.4]
INITIAL_ROTATION = [0, -1, 0, 0]

BLACK_START = Colors.BLACK, [0, 2e-5, 0.25], [0, -1, 0.25]
WHITE_START = Colors.WHITE, [0, -1, 0.25], [0, 2e-5, 0.25]


class Epoch(Base):
    """An epoch designed to run the T-Maze task evolution."""

    # initialize some variables used during epoch run to restart controller
    duration, counter = 150, 0

    def __init__(self, robot: EPuck):
        Base.__init__(self, robot, TMaze)

        # get position and rotation fields of robot controller
        self.robot_node = self.robot.getFromDef('evolvable')
        self.translation_field = self.robot_node.getField('translation')
        self.rotation_field = self.robot_node.getField('rotation')

    def step(self):
        """
        Run a step of the robot and collect its result/fitness in it.
        Periodically run the task again with random selected side to reach
        (defined by starting floor color)
        """

        if not self.counter % self.duration:

            # reset robot to start position
            self.translation_field.setSFVec3f(INITIAL_POSITION)
            self.rotation_field.setSFRotation(INITIAL_ROTATION)

            # ensure that changes take place
            self.robot_node.resetPhysics()
            self.robot.step(self.robot.run_frequency.ms)

            # get floors transaction fields
            light = self.robot.getFromDef('light_floor').getField('translation')
            dark = self.robot.getFromDef('dark_floor').getField('translation')

            # randomly set a floor as starting one (basically, hide the other)
            if random.randint(0, 1):
                starting_color, black_position, white_position = WHITE_START
            else:
                starting_color, black_position, white_position = BLACK_START
            light.setSFVec3f(white_position)
            dark.setSFVec3f(black_position)

            # (re)set initial color of evaluator utils
            self.evaluator.initial_color = starting_color

        # call super step
        Base.step(self)

        # increment counter
        self.counter += 1


def new_epoch(robot: EPuck) -> Epoch: return new(robot, Epoch)


def evolve_epoch(epoch: Epoch) -> Epoch: return evolve(epoch, Epoch)
