from control.adapt import adapt
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

    # backup the current Tsetlin state
    state = replica.tsetlin.state.type

    # decide the working strategy at the next epoch according to the previous best and current performance
    replica.tsetlin.transit(replica.configuration.performance, replica.history.best_configuration.performance)

    # if the last configuration had better performance than the best known one, set it as the new best
    if replica.configuration.performance > replica.history.best_configuration.performance:
        replica.history.best_configuration = replica.configuration

    # adapt the control configuration of the replica
    replica.configuration = adapt(replica)

    return replica


__all__ = "run_epoch",
