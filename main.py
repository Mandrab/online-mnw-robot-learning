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
