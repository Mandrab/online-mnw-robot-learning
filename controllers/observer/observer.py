from functools import reduce
from evaluation import evaluate_step
from inout import save
from player.inout import configs


EPOCHS_COUNT = configs["task"]["epochs_count"]
STEPS_COUNT = configs["task"]["epochs_duration"]
REPLICAS_COUNT = configs["task"]["replicas_count"]


# evaluate an epoch by evaluating each of its steps (the performance of each step are collected)
evaluate_epoch = lambda _: reduce(
    # concat the performance of each step
    lambda acc, val: (acc[0] + val[:1], acc[1] + val[1:]),
    # evaluate the performance of the group of robots at each step of an epoch
    map(evaluate_step, range(STEPS_COUNT)),
    # the evaluation starts with no information (i.e., performance)
    ([], [])
)

# evaluate a replica by evaluating each of its epochs and by saving the results
evaluate_replica = lambda _: list(map(save, map(evaluate_epoch, range(EPOCHS_COUNT))))

# run a simulation evaluating each of its replicas
evaluate_simulation = list(map(evaluate_replica, range(REPLICAS_COUNT)))
