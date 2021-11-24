""" CONFIGURATION OF ROBOT MODULES """

from components import sensors, motors

used_sensors = [
    # front
    sensors['A335'],
    sensors['A25'],

    # side
    sensors['A45'],
    sensors['A90'],
    sensors['A315'],
    sensors['A270']
]

used_actuators = [
    motors['LEFT'],
    motors['RIGHT']
]
