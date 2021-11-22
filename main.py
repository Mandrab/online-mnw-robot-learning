import subprocess

__WORLD_FILE = 'worlds/world.wbt'

################################################################################
# START OF SIMULATION

# start a simulation subprocess
subprocess.run([
    'webots',
    '--mode=fast',      # fast running
    '--no-rendering',   # disable rendering
    '--minimize',       # minimize the window on startup
    '--batch',          # does not create blocking pop-ups
    '--stdout',         # redirect robot out to stdout
    '--stderr',         # redirect robot errors to stderr
    '--log-performance=stdout',     # measure the performance
    __WORLD_FILE
], shell=True, check=True)

# ###############################################################################
# # ANALYSE & PLOTTING
#
# # inspect(graph)
#
# # plot.plot(evolution, plot.adj_matrix)
# # plot.plot(evolution, plot.network)
# # plot.plot(evolution, plot.graph)
# # plot.plot(evolution, plot.kamada_kawai_graph)
# # plot.plot(evolution, plot.degree_of_nodes)
# # plot.plot(evolution, plot.highlight_connected_components)
# # plot.plot(evolution, plot.largest_connected_component)
# # plot.plot(evolution, plot.network_7)
# # plot.plot(evolution, plot.conductance)
# # plot.plot(evolution, plot.voltage_distribution_map)
# # plot.plot(evolution, plot.conductance_map)
# # plot.plot(evolution, plot.information_centrality_map)
# # plot.plot(evolution, plot.outputs)
# # plot.plot(evolution, plot.animation)
# # plot.plot(evolution, plot.animation_kamada_kawai)
