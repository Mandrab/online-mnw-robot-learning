from conductor import Conductor
from config.simulation import *
from config.network import *
from epuck import EPuck
from evaluators import Distance, Fitness

################################################################################
# ROBOT SETUP

# crate robot controller
conductor = Conductor(graph, datasheet)

# create the Robot instance
robot = EPuck(conductor)

# randomly connect the actuators(motors) to the network
output_nodes = random_nodes(conductor.network, avoid=set(), count=2)
conductor.set_actuators(dict(zip(robot.motors, output_nodes)))

# get nodes distant 2 step from outputs nodes
source_selector = minimum_distance_selection([*output_nodes], distance=2)
viable_nodes = [*source_selector(conductor.network, [], -1)]

# randomly select input nodes between the ones that are suitable for the
# selection
# the selected nodes may be repeated
input_nodes = [
    viable_nodes[random.randrange(len(viable_nodes))] for _ in robot.sensors
]
conductor.set_sensors(dict(zip(robot.sensors, input_nodes)))

# initialize the network with the given setting
conductor.initialize()

################################################################################
# DEFINE SIMULATIONS UTILITIES

# contains graphs and distance obtained by the robot todo
results = []

################################################################################
# RUN THE SIMULATION

max_fitness = 0
connections = input_nodes

# simulate count epochs run
for epoch in range(epoch_count):
    print(f'Start of {epoch} simulation')

    # reset simulation to start point
    robot.simulationReset()
    robot.simulationSetMode(robot.SIMULATION_MODE_FAST)

    # used to accumulate performance in steps
    fitness = Fitness(robot)

    # used to compute travelled distance
    distance_evaluator = Distance(robot)

    # perform simulation steps until a epoch is completed
    for _ in range(epoch_duration):

        # run a simulation step
        robot.run()

        # update travelled distance
        distance_evaluator.update()

        # update fitness value
        fitness.update()

        # debugging plotting - to understand behaviour
        # e = Evolution(datasheet, {}, 0.5, set(), set(), [(graph, list())])
        # plot.plot(e, plot.voltage_distribution_map)

    # compute fitness
    print('fitness:', fitness.fitness())
    print('distance:', distance_evaluator.distance * 100)

    if fitness.fitness() > max_fitness:
        max_fitness = fitness.fitness()
        connections = input_nodes

    # randomly connect the sensors to the network
    input_nodes = mutate(
        graph=conductor.network,
        sources=input_nodes,
        ground=-1,
        probability=0.3,
        minimum_mutants=1,
        maximum_mutants=4,
        viable_node_selection=source_selector
    )
    conductor.set_sensors(dict(zip(robot.sensors, input_nodes)))

print("Running the best scoring controller")

conductor.set_sensors(dict(zip(robot.sensors, input_nodes)))

while True:
    robot.run()

################################################################################
# RESULT SAVE

# todo
