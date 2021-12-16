import subprocess
import sys

# get process parameters:
# - first: process name
# - second: world file's name
# - third: not expected parameters
_0, world_name, *_1 = *sys.argv, None

# define world file location and use default file if none is specified
__WORLD_FILE = f'worlds/{world_name or "main_world"}.wbt'

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
