import json
import re
import sys

_, input_filename, output_filename, *_ = sys.argv

print(f'Converting {input_filename} to json')

skip_lines = ['Generating network', 'Saving graph to file']
description_passed = False

jsons = list()

expression = 'Device density: ([0-9|\.]*), '
expression += 'Connected component density: ([0-9|\.]*), '
expression += 'Motor load: ([0-9|e\+]*), '
expression += 'Average sensor signal multiplication: ([0-9|\.]*)%'
head_pattern = re.compile(expression)

expression = 'fitness: (.*)'
body_pattern = re.compile(expression)

with open(input_filename) as infile:
    for line in infile.readlines():

        if results := head_pattern.search(line):
            density, cc_density, load, avg_multiplier = results.groups()
            configuration = dict(
                density=float(density),
                cc_density=float(cc_density),
                load=float(load),
                avg_multiplier=float(avg_multiplier),
                fitness=list()
            )
            jsons.append(configuration)

        if results := body_pattern.search(line):
            configuration['fitness'].append(float(results.group(1)))

with open(output_filename, mode='w') as file:
    json.dump(jsons, file, indent=4)
