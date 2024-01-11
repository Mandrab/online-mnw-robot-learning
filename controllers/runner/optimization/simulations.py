import random

from ctypes import c_double, c_int
from nnspy import datasheet, interface, nns
from optimization.biography import Biography
from optimization.individual import Individual
from optimization.simulation import Simulation
from optimization.task import Task
from optimization.tsetlin import tsetlin
from robot.body import EPuck
from robot.cortex import new as new_cortex
from robot.pyramid import random as random_pyramid
from robot.thalamus import random as random_thalamus
from typing import Iterable, Tuple

DEVICE_SIZE = 125
WIRES_LENGTH = 14.0


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

        # create a datasheet with the desired density
        ds = datasheet()
        ds.wires_count = int(density * size ** 2 / wires_length ** 2)
        ds.length_mean = wires_length
        ds.length_std_dev = wires_length * 0.35
        ds.package_size = size
        ds.generation_seed = seed

        random.seed(ds.generation_seed)

        cortex = new_cortex(ds)
        pyramid = random_pyramid(robot, cortex, load)
        thalamus = random_thalamus(robot, cortex, pyramid)
        biography = Biography(task.evaluator(robot))
        elite = Individual(robot, cortex, pyramid, thalamus, biography)

        return Simulation(elite, task, epoch_count, epoch_duration, tsetlin.reset())

    # lazily generate a simulation for each setting and return them
    return map(generate, device_configurations)


def save(data: Tuple[int, Individual]):
    """Save epoch information into files with the given format name"""

    index, instance = data

    it = interface()
    it.sources_count = len(instance.thalamus.mapping)
    it.sources_index = (c_int * it.sources_count)()
    it.grounds_count = 0
    it.grounds_index = (c_int * it.grounds_count)()
    it.loads_count = len(instance.pyramid.mapping)
    it.loads_index = (c_int * it.loads_count)()
    it.loads_weight = (c_double * it.loads_count)()

    for i, pin in enumerate(instance.pyramid.mapping.values()):
        it.loads_index[i] = pin
        it.loads_weight[i] = instance.pyramid.sensitivity

    for i, pin in enumerate(instance.thalamus.mapping.values()):
        it.sources_index[i] = pin

    ds, nt = instance.cortex.datasheet, instance.cortex.topology
    ns, cc = instance.cortex.state, instance.cortex.component

    nns.serialize_network(ds, nt, ".".encode('utf-8'), index)
    nns.serialize_state(ds, nt, ns, ".".encode('utf-8'), index, 0)
    nns.serialize_component(cc, ".".encode('utf-8'), index, 0)
    nns.serialize_interface(it, ".".encode('utf-8'), index, 0)
