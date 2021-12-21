from optimization.Fitness import Fitness
from nanowire_network_simulator import minimum_distance_selection
from nanowire_network_simulator import mutate, random_nodes
from robot.conductor import copy
from robot.epuck import EPuck
from typing import List, Dict, Callable


class Epoch:
    """Evaluate the quality of connections to a network"""

    def __init__(self, robot: EPuck, evaluator: Callable[[EPuck], Fitness]):
        # save robot to execute and controller for reference
        self.robot, self.controller = robot, robot.conductor

        # define evaluation utils
        self.evaluator = evaluator(robot)

        # define history-container utils
        self.stimulus: List[Dict[str, float]] = []
        self.response: List[Dict[str, float]] = []

        # reset simulation to start/initial point
        robot.simulationReset()

    def step(self):
        """Run a simulation step and exec the required evaluations"""
        self.robot.run()

        # update fitness value
        self.evaluator.update()

        # save sensor readings and motors speeds for future analysis
        self.stimulus += [{s: s.read() for s in self.robot.sensors}]
        self.response += [{m: m.speed for m in self.robot.motors}]


def new_epoch(robot: EPuck, builder: Callable[[EPuck], Epoch]) -> Epoch:
    """Instantiate a new evaluation run for a robot"""

    # get the controller from the robot
    graph = robot.conductor.network

    # select actuator nodes from the available nodes
    actuators = random_nodes(graph, set(), len(robot.motors))
    robot.conductor.actuators = dict(zip(robot.motors, actuators))

    # select source nodes from the ones that are at least 2 steps far from the
    # outputs nodes
    neighbor = minimum_distance_selection(actuators, 2, True)(graph, list(), -1)
    sensors = list(random_nodes(graph, neighbor, len(robot.sensors)))
    robot.conductor.sensors = dict(zip(robot.sensors, sensors))

    # initialize the network with the given setting
    robot.conductor.initialize()

    return builder(robot)


def evolve_epoch(epoch: Epoch, builder: Callable[[EPuck], Epoch]) -> Epoch:
    """
    Instantiate a new evaluation run for a robot as an evolution (in
    connections) of a previous one.
    """

    # avoid overwrite of controller's fields
    epoch.robot.conductor = copy(epoch.controller)

    # obtain the new sensors and set them in the conductor
    epoch.robot.conductor.sensors = dict(zip(epoch.robot.sensors, mutate(
        graph=epoch.controller.network,
        sources=list(epoch.controller.sensors.values()), ground=-1,
        probability=0.3, minimum_mutants=1, maximum_mutants=4,
        viable_node_selection=minimum_distance_selection(
            outputs=set(epoch.controller.actuators.values()),
            distance=2
        )
    )))

    # return the evolved epoch
    return builder(epoch.robot)
