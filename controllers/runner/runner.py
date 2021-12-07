import time

from conductor import Conductor
from config.simulation import *
from optimization.Simulation import Simulation
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import backup
from typing import List

DEVICE_SIZE = 50
WIRES_LENGTH = 10.0
SAVING_FOLDER = '../../res/configuration/'

# create a list of simulations to fill with each density simulation
simulations: List[Simulation] = []

# for each density, create and test a device as a controller
for density in densities:

    # calculate number of needed wires
    wires = int(density * DEVICE_SIZE ** 2 / WIRES_LENGTH ** 2)
    print('Network density:', density, 'wires:', wires)

    # define network characteristics
    datasheet = Datasheet(
        wires_count=wires,
        Lx=DEVICE_SIZE, Ly=DEVICE_SIZE,
        mean_length=WIRES_LENGTH, std_length=WIRES_LENGTH * 0.35
    )

    # set simulation to fast mode
    robot.simulationSetMode(robot.SIMULATION_MODE_FAST)

    # instantiate simulation with the given controller/device
    simulation = Simulation(robot, datasheet)

    # simulate count-epochs run
    for epoch in range(epoch_count):
        simulation.simulate(epoch_duration)

    # save simulation results
    simulations += [simulation]

print("Running the best scoring controller")
robot.simulationReset()

# get the best configurations found for each controller
bests = list(map(lambda s: s.best_epoch, simulations))

# save the configurations in a file
for index, epoch in enumerate(bests):
    c: Conductor = epoch.controller
    ms_time = time.time()
    backup.save(
        c.datasheet, c.network, c.wires,
        f'{SAVING_FOLDER}datasheet.{ms_time}.{index}.dat',
        f'{SAVING_FOLDER}network.{ms_time}.{index}.dat',
        f'{SAVING_FOLDER}wires.{ms_time}.{index}.dat'
    )

# get the best configuration overall
best = max(bests, key=lambda e: e.fitness.value())

# run the best controller until it is stopped
robot.conductor = best.controller
while robot.run():
    pass
