import json

from nanowire_network_simulator import backup
from nanowire_network_simulator.model.device.datasheet import factory as ds
from optimization.Epoch import Epoch
from optimization.Simulation import Simulation
from optimization.task.Tasks import Tasks
from os import listdir
from os.path import join, isfile, exists
from robot.conductor import Conductor
from robot.epuck import EPuck
from typing import Iterable, List, Tuple

DEVICE_SIZE = 50
WIRES_LENGTH = 10.0
READING_FOLDER = 'controllers/'


def new_simulations(
        robot: EPuck,
        configurations: List[Tuple[float, float, int]],
        size: int = DEVICE_SIZE,
        wires_length: float = WIRES_LENGTH,
        task_type: Tasks = Tasks.COLLISION_AVOIDANCE
) -> Iterable[Simulation]:
    """
    Generate a simulations set with each instance using a device with a
    different nano-wires density and seed.
    """

    def generate(setting):
        """Create device datasheet and use it to instantiate the simulation."""
        density, motors_load, seed = setting
        datasheet = ds.from_density(density, size, wires_length, seed)
        simulation = Simulation(robot, datasheet, task_type=task_type)
        simulation.motor_load = motors_load
        return simulation

    # lazily generate a simulation for each setting and return them
    return map(generate, configurations)


def import_simulations(
        robot: EPuck,
        folder: str = READING_FOLDER,
        task_type: Tasks = Tasks.COLLISION_AVOIDANCE
) -> Iterable[Simulation]:
    """
    Check if there are simulations files in the given folder.
    Return an iterable with the imported simulations instances.
    If the folder does not exists or if there are not files, return an empty
    list.
    """

    # check that the folder exists
    if not exists(folder):
        return []

    # find files in the given folder
    files = filter(isfile, map(lambda s: join(folder, s), listdir(folder)))

    # get data files (exclude any other extension file)
    files = list(filter(lambda _: _.endswith('.dat'), files))

    # if the folder does not contains data files, return an empty list
    # this is needed to identify lack of instances without import all the graphs
    if not files:
        return []

    # sort them by simulation index (pre-extension)
    files = sorted(files, key=lambda _: _.split('.')[-2])

    # take chunks of 6 (number of simulations files)
    chunks = map(lambda i: sorted(files[i*6:][:6]), range(int(len(files) / 6)))

    # discard sensors/actuators history files (indexes: 0, 4) & order others
    chunks = map(lambda _: _[1:][:2] + _[-1:] + _[:1], chunks)

    # convert files to python data
    chunks = map(lambda _: backup.read(*_), chunks)

    # instantiate simulation with the given controller/device
    def simulation(settings: Tuple) -> Simulation:
        graph, datasheet, wires, io = settings
        return Simulation(robot, datasheet, (graph, wires, io), task_type)

    # return a lazy mapping to the simulations
    return map(simulation, chunks)


def save_epoch(epoch: Epoch, file_format: str = '{name}.dat'):
    """Save epoch information into files with the given format name"""

    c: Conductor = epoch.controller

    # save controller characteristics
    backup.save(
        c.datasheet, c.network, c.wires,
        dict(inputs=c.sensors, outputs=c.actuators, load=c.load),
        file_format.format(name='datasheet'),
        file_format.format(name='network'),
        file_format.format(name='wires'),
        file_format.format(name='connections')
    )

    # save sensor/motor states during the simulation
    with open(file_format.format(name='stimulus'), 'w') as file:
        json.dump(epoch.stimulus, file)
    with open(file_format.format(name='response'), 'w') as file:
        json.dump(epoch.response, file)
