import random

from optimization.Epoch import Epoch as Base
from optimization.Epoch import new_epoch as new, evolve_epoch as evolve
from optimization.task.tmaze.fitness import TMaze
from robot.epuck import EPuck

INITIAL_POSITION = [0, 0, 0.4]
INITIAL_ROTATION = [0, -1, 0, 0]


class Epoch(Base):
    """An epoch designed to run the T-Maze task evolution."""

    # initialize some variables used during epoch run to restart controller
    duration, counter = 150, 0

    def __init__(self, robot: EPuck):
        Base.__init__(self, robot, TMaze)

        # get position and rotation fields of robot controller
        node = self.robot.getFromDef('evolvable')
        self.translation_field = node.getField('translation')
        self.rotation_field = node.getField('rotation')

    def step(self):
        # every 'duration' steps, reset robot position and run the task again
        # with random selected side to reach (defined by starting floor color)
        if not self.counter % self.duration:

            # get floors transaction fields
            light = self.robot.getFromDef('light_floor').getField('translation')
            dark = self.robot.getFromDef('dark_floor').getField('translation')

            # randomly swap initial floors positions (basically, hide one)
            if random.randint(0, 1):
                light_level, dark_level = light.getSFVec3f(), dark.getSFVec3f()
                light.setSFVec3f(dark_level)
                dark.setSFVec3f(light_level)

            # reset robot to start position
            self.translation_field.setSFVec3f(INITIAL_POSITION)
            self.rotation_field.setSFRotation(INITIAL_ROTATION)

            # notify evaluator that a new run is starting
            self.evaluator.reset()

        # increment counter
        self.counter += 1

        # call super step
        Base.step(self)


def new_epoch(robot: EPuck) -> Epoch: return new(robot, Epoch)


def evolve_epoch(epoch: Epoch) -> Epoch: return evolve(epoch, Epoch)
