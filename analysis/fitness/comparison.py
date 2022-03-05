import json
import sys

from fitness import *


def get_data(path):
    with open(path) as file:
        return json.load(file)


folder = f'res/{sys.argv[1]}/'
data = [(a, b) for a, b in [tuple(_.split('=')) for _ in sys.argv[2:]]]

data = [(a, get_data(folder + b + '/dataset.json')) for a, b in data]

data = {a: [max(_['fitness']) for _ in b] for a, b in data}

title = 'Fitness distribution according to input pre-processing'
boxplot(title, 'Density', 'Fitness', data)
