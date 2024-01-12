from replica import Replica, run
from task import evaluate
from typing import Tuple


def step(replica_performance: Tuple[Replica, float], _: int) -> Tuple[Replica, float]:

    # decompose the input data
    replica, performance = replica_performance

    # run this replica in a simulation step
    run(replica)

    # evaluate the replica performance in this simulation step
    performance += evaluate()

    # returns the replica with the updated performance evaluation
    return replica, performance
