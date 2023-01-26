from logger import logger
from optimization.fitness import Fitness as Base

PENALTY = -50
PRIZE = 50


def _fitness(gripper, prey_sensor, ground_sensor) -> float:

    # no state change correspond to 0 fitness
    if not gripper.state_changed:
        return .0

    # calculate if the robot is on the nest
    on_nest = ground_sensor.value < 500

    # if the gripper closes with a prey in front, prize it
    if gripper.close and prey_sensor.value:

        logger.info("capture")
        return PRIZE

    # 'prey is not None' cannot be evaluated by the robot directly.
    # It represents the perception of the object in front of the robot after the gripper opening.
    # However, due to the actual structure of the experiment, it cannot be evaluated
    # and a trick is therefore needed.
    if not gripper.close and gripper.prey is not None:

        if on_nest:
            logger.info("correct deposit")
            return PRIZE
        else:
            logger.info("wrong deposit")
            return PENALTY

    return 0


class Fitness(Base):
    """Calculate the fitness depending on collision avoidance capabilities together with the foraging behavior."""

    fitness: float = 0.0
    counter: int = 0

    def update(self):

        # separate different type of sensors
        ps = next(filter(lambda sensor: sensor.startswith('prey-sensor'), self.robot.sensors))
        gs = next(filter(lambda sensor: sensor.startswith('gs0'), self.robot.sensors))

        # separate gripper and motor actuators
        a = next(filter(lambda actuator: actuator.startswith('gripper'), self.robot.motors))

        # calculate the foraging fitness
        self.fitness += _fitness(a, ps, gs)

        self.counter += 1

    def value(self) -> float: return self.fitness
