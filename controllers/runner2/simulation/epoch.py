from control.adapt import adapt
from control.tsetlin.state import State
from functools import reduce
from inout.loader import configs
from inout.logger import logger
from simulation.history import Adaptation
from simulation.replica import Replica
from task import step
from webots.supervisor import supervisor

CONTINUOUS_EXPERIMENT: bool = configs["task"]["continuous"]
EPOCHS_DURATION: int = configs["task"]["epochs_duration"]
HISTORY_WEIGHT: float = configs["task"]["history_weight"]


def run_epoch(replica: Replica, _: int) -> Replica:

    # restore simulation to starting point if the task is not continuous
    if not CONTINUOUS_EXPERIMENT:
        supervisor.simulationReset()

    # run the replica for the specified number of steps and collect the performance
    replica = reduce(step, range(EPOCHS_DURATION), replica)

    # log the performance to console and to file
    logger.info(f"performance: {replica.configuration.performance}")

    # save the information relative to the current epoch
    replica.history.append(Adaptation(replica.configuration, replica.tsetlin.state.type, replica.tsetlin.state_idx))

    # if the best known configuration is in use, update its overall evaluation
    if replica.tsetlin.state.type == State.Type.OPERATION:
        replica.history.best_configuration.performance *= HISTORY_WEIGHT
        replica.history.best_configuration.performance += (1 - HISTORY_WEIGHT) * replica.configuration.performance
    # if a new configuration is in use and its performance is higher than the best known one, set it as the new best
    elif replica.configuration.performance > replica.history.best_configuration.performance:
        replica.history.best_configuration = replica.configuration

    # adapt the control configuration of the replica
    replica.configuration = adapt(replica)

    return replica


__all__ = "run_epoch",
