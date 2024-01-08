"""
Converts the readme file of a run to a json dataset for an easier analysis.
"""

import json
import re
import sys

_, input_filename, output_filename, *_ = *sys.argv, 'README.md', 'dataset.json'

print(f'Converting {input_filename} to json')

json_objects = list()

expression = 'Device density: ([0-9|\.]*), '
expression += 'CC #wires: ([0-9|\.]*), '
expression += 'CC #junctions: ([0-9|\.]*), '
expression += 'Motor load: ([0-9|e\+]*), '
expression += 'Average sensor signal multiplication: ([0-9|\.]*)%'

head_pattern = re.compile(expression)
body_pattern = re.compile('fitness: (.*)')

with open(input_filename) as infile:
    for line in infile.readlines():

        # standard format of readme files
        if results := head_pattern.search(line):
            density, cc_wires, cc_junctions, load, avg_multiplier, *_ = results.groups()
            configuration = dict(
                density=float(density),
                cc_wires=int(cc_wires),
                cc_junctions=int(cc_junctions),
                load=float(load),
                avg_multiplier=float(avg_multiplier),
                fitness=list()
            )
            json_objects.append(configuration)

        # iteration fitness line
        if results := body_pattern.search(line):
            configuration['fitness'].append(float(results.group(1)))

with open(output_filename, mode='w') as file:
    json.dump(json_objects, file, indent=4)
