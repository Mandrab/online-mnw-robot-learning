from conductor import Conductor
from config.simulation import *
from evaluators import Distance, Fitness
from nanowire_network_simulator.model.device import Datasheet
from nanowire_network_simulator import random_loads, random_nodes,\
    minimum_viable_network, minimum_distance_selection, mutate

max_fitness = -1
network = None, None
inputs, outputs = None, None

for (wires, size, length), (raw_signals, network_range) in grid:
    print(
        f'Wires:', wires, 'wire length:', length, 'dev. size:', size,
        'raw signal (not distance):', raw_signals,
        'network input range:', network_range
    )

    datasheet = Datasheet(
        wires_count=wires,
        Lx=size,
        Ly=size,
        mean_length=length,
        std_length=length / 2.0,
    )
    # create a device that is represented by the given datasheet
    graph, _ = minimum_viable_network(datasheet)

    # INTERFACING

    # select a random ground node
    grounds = random_nodes(graph, avoid=set())

    # select source nodes from non-grounds nodes
    sources = random_nodes(graph, grounds, count=4)

    # select output nodes from non-grounds & non-source nodes # todo distance
    loads = random_loads(graph, grounds | sources, count=2)

    # crate robot controller
    robot.conductor = Conductor(graph, datasheet)
    robot.conductor.stimulus_range = network_range

    # randomly connect the actuators(motors) to the network
    output_nodes = random_nodes(graph, avoid=set(), count=2)
    robot.conductor.actuators = dict(zip(robot.motors, output_nodes))

    # get nodes distant 2 step from outputs nodes
    source_selector = minimum_distance_selection([*output_nodes], distance=2)
    viable_nodes = [*source_selector(graph, [], -1)]

    # randomly select input nodes between the ones that are suitable for the
    # selection
    # the selected nodes may be repeated
    input_nodes = [
        viable_nodes[random.randrange(len(viable_nodes))] for _ in robot.sensors
    ]
    robot.conductor.sensors = dict(zip(robot.sensors, input_nodes))

    # initialize the network with the given setting
    robot.conductor.initialize()

    # simulate count epochs run
    for epoch in range(epoch_count):
        # print(f'Start of {epoch} simulation')

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
            robot.run(raw_signals)

            # update travelled distance
            distance_evaluator.update()

            # update fitness value
            fitness.update()

            # debugging plotting - to understand behaviour
            # e = Evolution(datasheet, {}, 0.5, set(), set(), [(graph, list())])
            # plot.plot(e, plot.voltage_distribution_map)

        # compute fitness
        print(
            '\tfitness:', round(fitness.fitness(), 3),
            '\tdistance:', round(distance_evaluator.distance * 100, 3)
        )

        # if the connection is better, keep using it, otherwise use previous one
        if fitness.fitness() > max_fitness:
            max_fitness = fitness.fitness()
            network = graph, network_range
            inputs, outputs = input_nodes, output_nodes

        # randomly connect the sensors to the network
        input_nodes = mutate(
            graph=robot.conductor.network,
            sources=inputs,
            ground=-1,
            probability=0.3,
            minimum_mutants=1,
            maximum_mutants=4,
            viable_node_selection=source_selector
        )
        robot.conductor.sensors = dict(zip(robot.sensors, input_nodes))

print("Running the best scoring controller")

robot.conductor.network = network[0]
robot.conductor.stimulus_range = network[1]
robot.conductor.sensors = dict(zip(robot.sensors, inputs))
robot.conductor.actuators = dict(zip(robot.motors, outputs))

while True:
    robot.run()

################################################################################
# RESULT SAVE

# todo
