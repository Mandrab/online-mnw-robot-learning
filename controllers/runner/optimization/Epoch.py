from epuck import EPuck
from evaluators import Fitness, Distance
from nanowire_network_simulator import minimum_distance_selection,\
    random_nodes, mutate
from typing import List


class Epoch:
    """Evaluate the quality of connections to a network"""

    def __init__(self, robot: EPuck, sensors: List[int], actuators: List[int]):
        self.robot = robot

        # save connections to maintain epoch data
        self.sensors = sensors
        self.actuators = actuators

        # save the controller to avoid changes in the robot reference
        self.controller = robot.conductor

        # set sensors to the controller
        self.controller.sensors = dict(zip(self.robot.sensors, sensors))
        self.controller.actuators = dict(zip(self.robot.motors, actuators))

        # define evaluation utils
        self.fitness = Fitness(robot)
        self.distance = Distance(robot)

        # reset simulation to start/initial point
        robot.simulationReset()
        robot.simulationSetMode(robot.SIMULATION_MODE_FAST)

    def step(self):
        """Run a simulation step and exec the required evaluations"""
        self.robot.run()

        # update fitness value
        self.fitness.update()

        # update distance value
        self.distance.update()


def new_epoch(robot: EPuck) -> Epoch:
    """Instantiate a new evaluation run for a robot"""

    # get the controller from the robot
    graph = robot.conductor.network

    # select and set actuator nodes from the available nodes
    actuators = [*random_nodes(graph, set(), len(robot.motors))]
    robot.conductor.sensors = dict(zip(robot.motors, actuators))

    # select and set source nodes from the ones that are at least 2 steps
    # far from the outputs nodes
    neighbor = minimum_distance_selection(
        outputs=actuators,
        distance=2,
        take_neighbor=True
    )(graph, list(), -1)
    sensors = [*random_nodes(graph, avoid=neighbor, count=len(robot.sensors))]
    robot.conductor.sensors = dict(zip(robot.sensors, sensors))

    # initialize the network with the given setting
    robot.conductor.initialize()

    # return the new Epoch
    return Epoch(
        robot=robot,
        sensors=sensors,
        actuators=actuators
    )


def evolve_epoch(robot: Epoch) -> Epoch:
    """
    Instantiate a new evaluation run for a robot as an evolution (in
    connections) of a previous one.
    """

    # obtain the new sensors
    sensors = mutate(
        graph=robot.robot.conductor.network,
        sources=[*robot.controller.sensors.values()],
        ground=-1,
        probability=0.3,
        minimum_mutants=1,
        maximum_mutants=4,
        viable_node_selection=minimum_distance_selection(
            outputs=[*robot.robot.conductor.actuators.values()],
            distance=2
        )
    )

    # return the evolved epoch
    return Epoch(
        robot=robot.robot,
        sensors=sensors,
        actuators=robot.actuators
    )
