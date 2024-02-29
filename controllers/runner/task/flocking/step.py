from simulation.replica import Replica, run
from task.flocking.evaluator import evaluate


def step(replica: Replica, _: int) -> Replica:

    # run this replica in a simulation step
    run(replica)

    # evaluate the replica performance in this simulation step
    replica.configuration.performance += evaluate()

    # returns the replica with the updated performance evaluation
    return replica


__all__ = "step",
