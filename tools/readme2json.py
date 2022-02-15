"""
Converts the readme file of a run to a json dataset for an easier analysis.
"""

import itertools
import json
import re
import sys

_, input_filename, output_filename, *_ = sys.argv

print(f'Converting {input_filename} to json')

skip_lines = ['Generating network', 'Saving graph to file']
description_passed = False

json_objects = list()

expression = 'Device density: ([0-9|\.]*), '
expression += 'Connected component density: ([0-9|\.]*), '
expression += 'Motor load: ([0-9|e\+]*), '
expression += 'Average sensor signal multiplication: ([0-9|\.]*)%'

head_pattern = re.compile(expression)
head_pattern_0 = re.compile('Creation density: (.*), Connected.* density: (.*)')
head_pattern_1 = re.compile('Effective network density: (.*) wires.*')
body_pattern = re.compile('fitness: (.*)')
densities_pattern = re.compile(' *densities: (.*)')
load_pattern = re.compile(' *actuators resistance: (.*)')
replicas_pattern = re.compile(' *replicas: (.*)')

with open(input_filename) as infile:
    for line in infile.readlines():
        # get densities from line
        if results := densities_pattern.search(line):
            densities = map(float, json.loads(results.group(1)))
            densities = itertools.product(densities, range(replicas))
            densities = map(lambda _: _[0], densities)

        # get load from line
        if results := load_pattern.search(line):
            load = results.group(1)

        # get replicas from line
        if results := replicas_pattern.search(line):
            replicas = int(results.group(1))

        # standard (new) format of readme files
        if results := head_pattern.search(line):
            density, cc_density, load, avg_multiplier = results.groups()
            configuration = dict(
                density=float(density),
                cc_density=float(cc_density),
                load=float(load),
                avg_multiplier=float(avg_multiplier),
                fitness=list()
            )
            json_objects.append(configuration)

        # for old version of the readme files
        if results := head_pattern_0.search(line):
            density, cc_density = results.groups()
            configuration = dict(
                density=float(density),
                cc_density=float(cc_density),
                load=float(load),
                avg_multiplier=1.0,
                fitness=list()
            )
            json_objects.append(configuration)

        # for older version of the readme files
        if results := head_pattern_1.search(line):
            configuration = dict(
                density=float(next(densities)),
                cc_density=float(results.group(1)),
                load=float(load),
                avg_multiplier=1.0,
                fitness=list()
            )
            json_objects.append(configuration)

        # iteration fitness line
        if results := body_pattern.search(line):
            configuration['fitness'].append(float(results.group(1)))


with open(output_filename, mode='w') as file:
    json.dump(json_objects, file, indent=4)
