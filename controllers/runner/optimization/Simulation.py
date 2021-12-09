from conductor import Conductor
from epuck import EPuck
from nanowire_network_simulator import minimum_viable_network as generator
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from optimization.Epoch import Epoch, new_epoch, evolve_epoch
from typing import Dict, Tuple


class Simulation:
    """
    Simulate a robot moving in an environment with a with a given controller.
    Evaluate its behaviour and call for its optimization.
    """
    best_epoch: Epoch = None

    def __init__(
            self,
            robot: EPuck,
            datasheet: Datasheet,
            network: Tuple[Graph, Dict, Dict] = None
    ):
        """
        Setup the simulation creating a controller network and assigning it to
        the robot.
        If the network variable is not None, the simulator will use that
        controller for the first run. In that case, an evaluation duration is
        needed.
        """

        self.robot = robot

        # create/get a device that is represented by the given datasheet
        graph, wires = generator(datasheet) if network is None else network[:2]

        # crate robot controller to interact with the device
        self.controller = Conductor(graph, datasheet, wires)

        # finally set the controller to the robot
        robot.conductor = self.controller

        # define first epoch to test
        self.best_epoch = epoch = new_epoch(self.robot)

        # if specified, set connections
        if network is not None:
            inputs, outputs = network[2]['inputs'], network[2]['outputs']
            epoch.controller.sensors = dict(zip(robot.sensors, inputs))
            epoch.controller.actuators = dict(zip(robot.motors, outputs))

    def initialize(self, duration: int):
        self.__run(self.best_epoch, duration)

    def simulate(self, duration: int):
        """Evaluate the controller behaviour running different connections"""

        if self.best_epoch.fitness.value() < 50:
            # setup a new simulation's epoch
            epoch = new_epoch(self.robot)
        else:
            # evolve best network
            epoch = evolve_epoch(self.best_epoch)

        # run the simulation of this epoch
        self.__run(epoch, duration)

    def __run(self, epoch: Epoch, duration: int):
        # iterate for the epoch duration
        for _ in range(duration):
            epoch.step()

        # if the connection is better than the best one, start to evolve it
        if self.best_epoch.fitness.value() <= epoch.fitness.value():
            self.best_epoch = epoch

        print('fitness:', epoch.fitness.value())
