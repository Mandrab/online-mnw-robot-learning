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
        # no interaction with a prey correspond to 0 fitness
        if not gripper.state_changed or gripper.prey_index < 0:
            return

        # if the gripper closes with a prey under it, prize it
        if gripper.close:
            logger.info("capture")
            self.fitness += PRIZE

        # 'prey is not None' cannot be evaluated by the robot directly.
        # It represents the perception of the object in front of the robot after the gripper opening.
        # However, due to the actual structure of the experiment, it cannot be evaluated
        # and a trick is therefore needed.
        else:
            logger.info(f"{'correct' if on_nest(self.robot) else 'wrong'} deposit")
            self.fitness += (2 * PRIZE) if on_nest(self.robot) else PENALTY

    def value(self) -> float: return self.fitness
