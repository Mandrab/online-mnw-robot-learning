from functools import reduce
from inout.loader import configs
from inout.logger import logger
from inout.saver import save
from simulation.epoch import run_epoch
from simulation.replica import Replica, random_replica

STARTING_SEED = configs["task"]["starting_seed"]
REPLICAS_COUNT = configs["task"]["replicas_count"]
EPOCHS_COUNT = configs["task"]["epochs_count"]

# generate new replicas, each with its own control (they have different seeds)
replicas = map(random_replica, range(STARTING_SEED, STARTING_SEED + REPLICAS_COUNT))


def describe(replica: Replica) -> Replica:
    logger.info(replica.network)
    logger.info(f"new phase: {replica.tsetlin.state.type} (idx: {replica.tsetlin.state_idx})")
    return replica


# describe all the replica controllers
replicas = map(describe, replicas)

# run each replica for the specified number of epochs, adapting it each time
replicas = map(lambda x: reduce(run_epoch, range(EPOCHS_COUNT), x), replicas)

# commit the save of each replica results
list(map(save, enumerate(replicas)))

# end of the simulation
logger.info("Simulation complete")