from conductor import Conductor
from epuck import EPuck
from nanowire_network_simulator import minimum_viable_network
from nanowire_network_simulator.model.device import Datasheet
from optimization.Epoch import Epoch, new_epoch, evolve_epoch
from typing import List, Tuple


class Simulation:
    """
    Simulate a robot moving in an environment with a with a given controller.
    Evaluate its behaviour and call for its optimization.
    """

    epochs: List[Epoch] = []
    best_epoch: Epoch = None

    def __init__(
            self,
            robot: EPuck,
            datasheet: Datasheet,
            network_range: Tuple[float, float]
    ):
        """
        Setup the simulation creating a controller network and assigning it to
        the robot.
        """
        self.robot = robot

        # create a device that is represented by the given datasheet
        graph, _ = minimum_viable_network(datasheet)

        # crate robot controller
        self.controller = Conductor(graph, datasheet)
        self.controller.stimulus_range = network_range

        # finally set the controller to the robot
        robot.conductor = self.controller

    def simulate(self, duration: int):
        """Evaluate the controller behaviour running different connections"""

        if self.best_epoch is None:
            # setup first simulation's epoch
            epoch = new_epoch(self.robot)
            self.best_epoch = epoch
        else:
            # evolve best network
            epoch = evolve_epoch(self.best_epoch)

        # add the epoch to the list
        self.epochs += [epoch]

        # iterate for the epoch duration
        for _ in range(duration):
            epoch.step()

        # if the connection is better than the pre-best one, start to evolve it
        if self.best_epoch.fitness.value() <= epoch.fitness.value():
            self.best_epoch = epoch
