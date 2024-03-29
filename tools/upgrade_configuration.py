"""
Converts old runs' datasets/configurations to new ones.
"""
import json
import os
import re
import sys

_, folder = sys.argv

print(f'Upgrading configuration in {folder} to json')

load_pattern = re.compile(' *actuators resistance: (.*)')
sensor_pattern = re.compile(' *sensors range: (.*)')
tuple_extractor = re.compile('\[[0-9]+[, |-](.*)]')

files = os.listdir(folder)

with open(folder + next(_ for _ in files if _ == 'README.md')) as infile:

    for line in infile.readlines():

        # get load from line
        if results := load_pattern.search(line):
            load = float(results.group(1))

        # get sensors ranges
        if results := sensor_pattern.search(line):
            data = results.group(1).split(', ')
            data = [float(_.removeprefix('[').removesuffix(']')) for _ in data]
            data = [
                4095 / 1550 if _ == 7
                else 1 if _ == 4095             # no multiplier
                else 0 if _ == 0 else 4095 / _  # lower bound; multiplier
                for _ in data
            ]
            _, ir_multiplier, *data = data
            if data:
                _, ground_multiplier = data


for filename in filter(lambda _: 'connections' in _, files):

    # load and modify configuration
    with open(folder + filename) as file:
        configuration = json.load(file)

        # add load to configuration
        if 'load' not in configuration:
            configuration['load'] = load

        # add multiplier to configuration
        if 'multiplier' not in configuration:
            multipliers = list(configuration['inputs'])
            multipliers = {
                _: ir_multiplier if 'ps' in _ else ground_multiplier
                for _ in multipliers
            }
            configuration['multiplier'] = multipliers

    # save modified configuration
    with open(folder + filename, mode='w') as file:
        json.dump(configuration, file, indent=4)
