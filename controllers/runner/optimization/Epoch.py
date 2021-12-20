from optimization.Fitness import Fitness
from nanowire_network_simulator import minimum_distance_selection
from nanowire_network_simulator import mutate, random_nodes
from robot.conductor import copy
from robot.epuck import EPuck
from typing import List, Dict, Callable


class Epoch:
    """Evaluate the quality of connections to a network"""

    def __init__(
            self,
            robot: EPuck,
            sensors: List[int],
            actuators: List[int],
            evaluator: Callable[[EPuck], Fitness]
    ):
        # save data used during epoch run (it works as a log of states)
        self.robot, self.sensors, self.actuators = robot, sensors, actuators

        # save the controller to avoid changes in the robot reference
        self.controller = robot.conductor

        # set sensors to the controller
        self.controller.sensors = dict(zip(self.robot.ir_sensors, sensors))
        self.controller.actuators = dict(zip(self.robot.motors, actuators))

        # define evaluation utils
        self.evaluator = evaluator(robot)

        # define history-container utils
        self.stimulus: List[Dict[str, float]] = []
        self.response: List[Dict[str, float]] = []

        # reset simulation to start/initial point
        robot.simulationReset()

    def step(self):
        """Run a simulation step and exec the required evaluations"""

        self.robot.run(False)  # todo make configurable (e.g., raw_signals)

        # update fitness value
        self.evaluator.update()

        # save sensor readings and motors speeds for future analysis
        self.stimulus += [{s: s.read(False) for s in self.robot.ir_sensors}]
        self.response += [{m: m.speed for m in self.robot.motors}]


def new_epoch(
        robot: EPuck,
        builder: Callable[[EPuck, List[int], List[int]], Epoch]
) -> Epoch:
    """Instantiate a new evaluation run for a robot"""

    # get the controller from the robot
    graph = robot.conductor.network

    # select and set actuator nodes from the available nodes
    actuators = random_nodes(graph, set(), len(robot.motors))
    robot.conductor.sensors = dict(zip(robot.motors, actuators))

    # select and set source nodes from the ones that are at least 2 steps
    # far from the outputs nodes
    neighbor = minimum_distance_selection(
        outputs=actuators,
        distance=2,
        negate=True
    )(graph, list(), -1)
    sensors = [*random_nodes(graph, neighbor, len(robot.ir_sensors))]
    robot.conductor.sensors = dict(zip(robot.ir_sensors, sensors))

    # initialize the network with the given setting
    robot.conductor.initialize()

    # return the new Epoch
    return builder(robot, sensors, [*actuators])


def evolve_epoch(
        epoch: Epoch,
        builder: Callable[[EPuck, List[int], List[int]], Epoch]
) -> Epoch:
    """
    Instantiate a new evaluation run for a robot as an evolution (in
    connections) of a previous one.
    """

    # obtain the new sensors
    sensors = mutate(
        graph=epoch.controller.network,
        sources=[*epoch.controller.sensors.values()], ground=-1,
        probability=0.3, minimum_mutants=1, maximum_mutants=4,
        viable_node_selection=minimum_distance_selection(
            outputs={*epoch.controller.actuators.values()},
            distance=2
        )
    )

    # avoid overwrite of controller's fields
    epoch.robot.conductor = copy(epoch.controller)

    # return the evolved epoch
    return builder(epoch.robot, sensors, epoch.actuators)
