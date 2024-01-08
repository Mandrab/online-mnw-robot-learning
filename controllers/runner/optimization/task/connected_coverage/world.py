from logger import logger
from optimization.individual import Individual
from robot.robot import run


def live(instance: Individual, duration: int):
    """
    Evaluate the individual in the foraging task.
    Runs the robot and collect the resulting score of the step.
    """

    # iterate for the epoch duration
    for counter in range(duration):

        # run the individual
        stimulus, response = run(instance)

        # save the biography for the step
        instance.biography.evaluator.update()
        instance.biography.stimulus.append(stimulus)
        instance.biography.response.append(response)

    logger.info('fitness: ' + str(instance.biography.evaluator.value()))
