import json

from nanowire_network_simulator import backup
from nanowire_network_simulator.model.device.datasheet import factory as ds
from optimization.biography import Biography
from optimization.individual import Individual
from optimization.simulation import Simulation
from optimization.task import Task
from os import listdir
from os.path import join, isfile, exists
from robot.robot import unroll
from robot.body import EPuck
from robot.cortex import new as new_cortex, Cortex
from robot.pyramid import random as random_pyramid, Pyramid
from robot.thalamus import random as random_thalamus, Thalamus
from typing import Iterable, Tuple

DEVICE_SIZE = 125
WIRES_LENGTH = 14.0
READING_FOLDER = 'controllers/'


def new_simulations(
        robot: EPuck,
        simulation_configuration: Tuple[Task, int, int],
        device_configurations: Iterable[Tuple[float, float, int]],
        size: int = DEVICE_SIZE, wires_length: float = WIRES_LENGTH,
) -> Iterable[Simulation]:
    """
    Generate a simulations set with each instance using a device with a
    different nanowires density, seed and load.
    """

    task, epoch_count, epoch_duration = simulation_configuration

    def generate(setting: Tuple[float, float, int]):
        """Create device datasheet and use it to instantiate the simulation."""

        density, load, seed = setting
        datasheet = ds.from_density(density, size, wires_length, seed)

        cortex = new_cortex(datasheet)
        pyramid = random_pyramid(robot, cortex, load)
        thalamus = random_thalamus(robot, cortex, pyramid)
        biography = Biography(task.evaluator(robot))
        elite = Individual(robot, cortex, pyramid, thalamus, biography)

        return Simulation(elite, task, epoch_count, epoch_duration)

    # lazily generate a simulation for each setting and return them
    return map(generate, device_configurations)


def import_simulations(
        robot: EPuck,
        simulation_configuration: Tuple[Task, int, int],
        folder: str = READING_FOLDER
) -> Iterable[Simulation]:
    """
    Check if there are simulations files in the given folder.
    Return an iterable with the imported simulations instances.
    If the folder does not exist or if there are no files, return
    an empty list.
    """

    # check that the folder exists
    if not exists(folder):
        return []

    # find files in the given folder
    files = filter(isfile, map(lambda s: join(folder, s), listdir(folder)))

    # get data files (exclude any other extension file)
    files = list(filter(lambda _: _.endswith('.dat'), files))

    # if the folder does not contain data files, return an empty list
    # this is needed to identify lack of instances without import all the graphs
    if not files:
        return []

    # sort them by simulation index (pre-extension)
    files = sorted(files, key=lambda _: int(_.split('.')[-2]))

    # take chunks of 6 (number of simulations files)
    chunks = map(lambda i: sorted(files[i*6:][:6]), range(int(len(files) / 6)))

    # discard sensors/actuators history files (indexes: 0, 4) & order others
    chunks = map(lambda _: _[1:][:2] + _[-1:] + _[:1], chunks)

    # convert files to python data
    chunks = map(lambda _: backup.read(*_), chunks)

    task, epoch_count, epoch_duration = simulation_configuration

    # instantiate simulation with the given controller/device
    def simulation(settings: Tuple) -> Simulation:
        graph, datasheet, wires, io = settings

        cortex = Cortex(graph, datasheet, wires)
        pyramid = Pyramid(io['outputs'], io['load'])
        multiplier = dict(zip(inputs := io['inputs'], [1] * len(inputs)))
        thalamus = Thalamus(inputs, io.get('multiplier', multiplier))
        biography = Biography(task.evaluator(robot))
        elite = Individual(robot, cortex, pyramid, thalamus, biography)

        return Simulation(elite, task, epoch_count, epoch_duration)

    # return a lazy mapping to the simulations
    return map(simulation, chunks)


def save(instance: Individual, file_format: str = '{name}.dat'):
    """Save epoch information into files with the given format name"""

    _, cortex, pyramid, thalamus = unroll(instance)

    # save controller characteristics
    backup.save(
        cortex.datasheet, cortex.network, cortex.wires,
        dict(
            inputs=thalamus.mapping,
            outputs=pyramid.mapping,
            load=pyramid.sensitivity,
            multiplier=thalamus.multiplier
        ),
        file_format.format(name='datasheet'),
        file_format.format(name='network'),
        file_format.format(name='wires'),
        file_format.format(name='connections')
    )

    # save sensor/motor states during the simulation
    with open(file_format.format(name='stimulus'), 'w') as file:
        json.dump(instance.biography.stimulus, file)
    with open(file_format.format(name='response'), 'w') as file:
        json.dump(instance.biography.response, file)
