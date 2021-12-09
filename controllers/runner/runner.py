import json
import time

from conductor import Conductor
from config.simulation import *
from optimization.Simulation import Simulation
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import backup
from os import listdir
from os.path import isfile, join

DEVICE_SIZE = 50
WIRES_LENGTH = 10.0
SAVING_FOLDER = '../../res/configuration/'
READING_FOLDER = 'controllers/'

################################################################################
# SETUP

# check if there are configurations to use and get their representing files
files = map(lambda s: join(READING_FOLDER, s), listdir(READING_FOLDER))
files = sorted(filter(isfile, files))
count = int(len(files) / 4)  # pairs of datasheet, graph, wires & connections
files = zip(
    files[count:][:count],      # datasheet
    files[2 * count:][:count],  # graph
    files[-count:],             # wires
    files[:count],              # connections
)

# if configurations have been found, use them; otherwise generate according to
# densities
if count > 0:
    print('Running found configurations')

    # load configurations from memory
    configurations = map(lambda _: backup.read(*_), files)

    # instantiate simulation with the given controller/device
    simulations = map(
        lambda _: Simulation(robot, _[1], (_[0], *_[2:])),
        configurations
    )
else:
    print('Running generated configurations')

    # calculate number of needed wires
    wires = [int(d * DEVICE_SIZE ** 2 / WIRES_LENGTH ** 2) for d in densities]

    # define network characteristics
    datasheets = [
        Datasheet(
            wires_count=w,
            Lx=DEVICE_SIZE, Ly=DEVICE_SIZE,
            mean_length=WIRES_LENGTH, std_length=WIRES_LENGTH * 0.35
        ) for w in wires
    ]

    # instantiate simulations with the given controllers/devices
    simulations = map(lambda d: Simulation(robot, d), datasheets)

simulations = list(simulations)

################################################################################
# SIMULATION

# run simulations of different devices
for i, simulation in enumerate(simulations):
    g, d = simulation.controller.network, simulation.controller.datasheet
    print(
        'Network density:',
        g.number_of_nodes() * d.mean_length * d.mean_length / (d.Lx * d.Ly)
        if count > 0 else densities[i],
        'wires:', g.number_of_nodes()
    )

    # initialize the first epoch
    simulation.initialize(epoch_duration)

    # simulate count-epochs run
    for epoch in range(epoch_count):
        simulation.simulate(epoch_duration)

################################################################################
# SAVE OF BEST CONTROLLERS FILES

# get the best configurations found for each controller
bests = list(map(lambda _: _.best_epoch, simulations))

# save the configurations in a file
for index, epoch in enumerate(bests):
    c: Conductor = epoch.controller
    ms_time = time.time()
    backup.save(
        c.datasheet, c.network, c.wires,
        dict(inputs=c.sensors, ouputs=c.actuators),
        f'{SAVING_FOLDER}datasheet.{ms_time}.{index}.dat',
        f'{SAVING_FOLDER}network.{ms_time}.{index}.dat',
        f'{SAVING_FOLDER}wires.{ms_time}.{index}.dat',
        f'{SAVING_FOLDER}connections.{ms_time}.{index}.dat',
    )
    with open(f'{SAVING_FOLDER}sensors.{ms_time}.{index}.dat', 'w') as file:
        json.dump(epoch.stimulus, file)
    with open(f'{SAVING_FOLDER}actuators.{ms_time}.{index}.dat', 'w') as file:
        json.dump(epoch.response, file)

################################################################################
# RUN OF THE BEST CONTROLLER

print('Running the best scoring controller')
robot.simulationReset()

# get the best configuration overall
best = max(bests, key=lambda e: e.fitness.value())

# run the best controller until it is stopped
robot.conductor = best.controller
while robot.run():
    pass
