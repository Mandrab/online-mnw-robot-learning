from dataclasses import dataclass
from nanowire_network_simulator import stimulate
from robot.body import EPuck
from robot.cortex import Cortex, describe as cortex2str
from robot.component.motor import Motor
from robot.thalamus import Thalamus, describe as thalamus2str
from typing import Dict, Tuple
from utils import adapt


@dataclass(frozen=True)
class Robot:
    """Represents the join of cortex, thalamus and body."""

    body: EPuck
    cortex: Cortex
    thalamus: Thalamus


def run(instance: Robot) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Execute a simulation step, stimulating the network with the sensors signals.
    Evaluate its response and use it to control the motors.
    """

    body, cortex, thalamus = instance.body, instance.cortex, instance.thalamus
    graph, datasheet = cortex.network, cortex.datasheet
    sensors, motors = thalamus.sensors, thalamus.motors

    # webots has stopped/paused the simulation
    if body.step(body.run_frequency.ms) == -1:
        return dict(), dict()

    # get normalized sensors readings: [0, 1]
    reads = {s: s.read(normalize=True) for s in body.sensors}

    # filter to get used sensors and get their readings in the correct range
    reads = [(sensors[k], v) for k, v in reads.items() if k in sensors]
    reads = [(k, adapt(v, out_range=cortex.working_range)) for k, v in reads]

    # define the pin-resistance/load pairs for the motors
    loads = [(pin, thalamus.sensitivity) for pin in motors.values()]

    # stimulate the network with the sensors inputs
    stimulate(graph, datasheet, body.run_frequency.s, reads, loads, set())

    # extract outputs from network and remap output values from 0, 10 to:
    #   -6.28, 6.28 for distance: 10 = far -> 6.28 = move straight
    #   6.28, -6.28 for proximity: 10 = near -> -6.28 = go away
    outs = [(motor, graph.nodes[pin]['V']) for motor, pin in motors.items()]
    outs = {k: adapt(v, in_range=cortex.working_range) for k, v in outs}

    # set the motors' speed according to its response
    for motor, value in zip(body.motors, map(outs.get, body.motors)):
        motor.speed = adapt(value, out_range=Motor.range(reverse=True))

    # return data for reference
    return dict(zip(sensors.keys(), dict(reads).values())), outs


def describe(robot: Robot):
    """Return a custom string representation of the object."""

    return str(cortex2str(robot.cortex) + ' ' + thalamus2str(robot.thalamus))
