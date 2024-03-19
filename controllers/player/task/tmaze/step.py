from inout.loader import configs
from itertools import cycle
from simulation.replica import Replica, run
from task.tmaze.colors import Colors
from task.tmaze.evaluator import evaluate
from webots.robot import get_actuators
from webots.supervisor import supervisor

EPOCH_DURATION = configs["task"]["epochs_duration"]

STARTS = cycle([
    (Colors.BLACK, [0, 2e-5, 0.4], [0, -1, 0.4]),   # black start
    (Colors.WHITE, [0, -1, 0.4],   [0, 2e-5, 0.4])  # white start
])


def step(replica: Replica, index: int) -> Replica:
    if index % int(EPOCH_DURATION / 4) == 0:

        # restore simulation to starting condition
        supervisor.simulationReset()
        supervisor.step(1)

        # randomly set a floor as starting one (basically, hide the other)
        starting_color, black_position, white_position = next(STARTS)
        supervisor.getFromDef("light_floor").getField("translation").setSFVec3f(white_position)
        supervisor.getFromDef("dark_floor").getField("translation").setSFVec3f(black_position)

        # wait for the physic system to stabilize
        list(get_actuators(supervisor).items())[0][1].setVelocity(.0)
        list(get_actuators(supervisor).items())[1][1].setVelocity(.0)
        for _ in range(100):
            supervisor.step(1)

        # (re)set initial color of evaluator utils
        evaluate.__dict__["initial_color"] = starting_color
        evaluate.__dict__["reach_flag"] = False

    # run this replica in a simulation step
    run(replica)

    # evaluate the replica performance in this simulation step
    replica.configuration.performance += evaluate()

    # returns the replica with the updated performance evaluation
    return replica


__all__ = "step",
