import subprocess

__WORLD_FILE = 'worlds/world_braitenberg.wbt'

################################################################################
# START OF SIMULATION

# start a simulation subprocess
subprocess.run([
    'webots ' +
    '--batch ' +        # does not create blocking pop-ups
    '--log-performance=stdout ' +   # measure the performance
    __WORLD_FILE
], shell=True, check=True)
