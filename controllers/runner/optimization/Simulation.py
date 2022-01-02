import random

from optimization.task.Tasks import Tasks
from robot.conductor import Conductor
from robot.epuck import EPuck
from nanowire_network_simulator import minimum_viable_network as generator
from nanowire_network_simulator.model.device import Datasheet
from networkx import Graph
from optimization.Epoch import Epoch
from typing import Dict, Tuple


class Simulation:
    """
    Simulate a robot moving in an environment with a with a given controller.
    Evaluate its behaviour and call for its optimization.
    """
    # minimum fitness needed to evolve an epoch instead of creating a new one
    MINIMUM_FITNESS = 30.0

    # optional motor load specific to the given run
    motor_load = None

    best_epoch: Epoch = None

    def __init__(
            self,
            robot: EPuck,
            datasheet: Datasheet,
            network: Tuple[Graph, Dict, Dict] = None,
            task_type: Tasks = Tasks.COLLISION_AVOIDANCE
    ):
        """
        Setup the simulation creating a controller network and assigning it to
        the robot.
        If the network variable is not None, the simulator will use that
        controller for the first run. In that case, an evaluation duration is
        needed.
        """

        # create/get a device that is represented by the given datasheet
        graph, wires = generator(datasheet) if network is None else network[:2]

        # crate robot controller to interact with the device and save it and the
        # robot instance itself
        self.robot, self.controller = robot, Conductor(graph, datasheet, wires)

        # finally set the controller to the robot
        robot.conductor = self.controller

        # define first epoch to test
        _, self.new_epoch, self.evolve_epoch, _ = task_type.value
        self.best_epoch = self.new_epoch(self.robot)

        # if specified, set connections
        if network is not None:
            self.best_epoch.controller.sensors = network[2]['inputs']
            self.best_epoch.controller.actuators = network[2]['outputs']

    def initialize(self, duration: int):
        # set controller random seed
        random.seed(self.controller.datasheet.seed)

        # set robot motors load if specified
        if self.motor_load is not None:
            self.robot.motors_load = self.motor_load

        # exec an initialization run
        self.__run(self.best_epoch, duration)

    def simulate(self, duration: int):
        """Evaluate the controller behaviour running different connections"""

        if self.best_epoch.evaluator.value() < self.MINIMUM_FITNESS:
            # setup a new simulation's epoch
            epoch = self.new_epoch(self.robot)
        else:
            # evolve best network
            epoch = self.evolve_epoch(self.best_epoch)

        # run the simulation of this epoch
        self.__run(epoch, duration)

    def __run(self, epoch: Epoch, duration: int):
        # iterate for the epoch duration
        for _ in range(duration):
            epoch.step()

        # if the connection is better than the best one, start to evolve it
        if self.best_epoch.evaluator.value() <= epoch.evaluator.value():
            self.best_epoch = epoch

        print('fitness:', epoch.evaluator.value())

    def __str__(self):
        """Return a custom representation of the object."""

        graph, data = self.controller.network, self.controller.datasheet
        area = data.Lx * data.Ly
        density = data.wires_count * data.mean_length ** 2 / area
        cc_density = graph.number_of_nodes() * data.mean_length ** 2 / area

        load = self.motor_load if self.motor_load else self.robot.motors_load

        return str(
            f'Creation density: {density}, ' +
            f'Connected component density: {cc_density}, ' +
            'Motors load: {:.0e}'.format(load)
        )
