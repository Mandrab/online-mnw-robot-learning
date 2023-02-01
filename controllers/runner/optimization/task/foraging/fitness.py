from logger import logger
from optimization.fitness import Fitness as Base
from optimization.task.foraging.util import on_nest, on_plate

PENALTY = -50
PRIZE = 50


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities together with the foraging behavior."""

    fitness: float = 0.0

    def update(self):
        gripper = next(filter(lambda actuator: actuator.startswith('gripper'), self.robot.motors))

        # no state change correspond to 0 fitness
        if not gripper.state_changed:
            return

        # if the gripper closes with a prey in front, prize it
        if gripper.close and on_plate(self.robot):
            logger.info("capture")
            self.fitness += PRIZE

# 2 40 00 00
        # 'prey is not None' cannot be evaluated by the robot directly.
        # It represents the perception of the object in front of the robot after the gripper opening.
        # However, due to the actual structure of the experiment, it cannot be evaluated
        # and a trick is therefore needed.
        elif not gripper.close and gripper.prey is not None:

            if on_nest(self.robot):
                logger.info("correct deposit")
                self.fitness += 2 * PRIZE
            else:
                logger.info("wrong deposit")
                self.fitness += PENALTY

    def value(self) -> float: return self.fitness
