from config.simulation import *
from optimization.Simulation import Simulation
from nanowire_network_simulator.model.device import Datasheet
from typing import List

simulations: List[Simulation] = []

for density in densities:

    size = 50
    length = 10.0
    wires = int(density * size * size / (length * length))

    print('Network density:', density, 'wires:', wires)

    # define network characteristics
    datasheet = Datasheet(
        wires_count=wires,
        Lx=size,
        Ly=size,
        mean_length=length,
        std_length=length * 0.35
    )

    robot.simulationSetMode(robot.SIMULATION_MODE_FAST)

    simulation = Simulation(robot, datasheet)

    # simulate count epochs run
    for epoch in range(epoch_count):
        simulation.simulate(epoch_duration)

    simulations += [simulation]

print("Running the best scoring controller")

robot.simulationReset()
robot.simulationSetMode(robot.SIMULATION_MODE_FAST)

scores = [(s.best_epoch.fitness.value(), s.best_epoch) for s in simulations]
_, best = next(iter(sorted(scores, key=lambda e: -e[0])))

robot.conductor = best.controller

while True:
    robot.run()
