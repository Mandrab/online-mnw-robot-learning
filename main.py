import subprocess
import sys

__WORLD_FILE = 'worlds/main_world.wbt'

# open different main worlds
if len(sys.argv) > 1:
    __WORLD_FILE = f'worlds/main_world_{sys.argv[1]}.wbt'

################################################################################
# START OF SIMULATION

# start a simulation subprocess
subprocess.run([
    'webots ' +
    '--mode=fast ' +        # fast running
    '--no-rendering ' +     # disable rendering
    '--minimize ' +         # minimize the window on startup
    '--batch ' +            # does not create blocking pop-ups
    '--stdout ' +           # redirect robot out to stdout
    '--stderr ' +           # redirect robot errors to stderr
    '--log-performance=stdout ' +   # measure the performance
    __WORLD_FILE
], shell=True, check=True)
