from dataclasses import dataclass
from nanowire_network_simulator import stimulate
from robot.body import EPuck
from robot.cortex import Cortex, describe as cortex2str
from robot.component.motor import Motor
from robot.fiber import nodes
from robot.pyramid import Pyramid, describe as pyramid2str
from robot.thalamus import Thalamus, describe as thalamus2str
from typing import Dict, Tuple
from utils import adapt


@dataclass(frozen=True)
class Robot:
    """
    Represents the body of the robot with its control system. The body parameter
    represents the part of the individual that are not involved in performing
    computations (e.g., motors). Although the sensors may be seen as an
    exception, those are included in the body abstraction. The cortex contains
    the nanowire-neural-network and consists in the main control center of the
    robot. The pyramid contains the descending motor pathways that control the
    actuators. The thalamus contains the ascending sensor pathways that bring
    the signals to the cortex.
    """

    body: EPuck
    cortex: Cortex
    pyramid: Pyramid
    thalamus: Thalamus


def unroll(instance: Robot) -> Tuple[EPuck, Cortex, Pyramid, Thalamus]:
    """Return the tuple representing the robot"""

    return instance.body, instance.cortex, instance.pyramid, instance.thalamus


def run(instance: Robot) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Execute a simulation step, stimulating the network with the sensors signals.
    Evaluate its response and use it to control the motors.
    """

    body, cortex, pyramid, thalamus = unroll(instance)
    network, datasheet = cortex.network, cortex.datasheet
    sensors, motors = thalamus.mapping, pyramid.mapping

    # webots has stopped/paused the simulation
    if body.step(body.run_frequency.ms) == -1:
        return dict(), dict()

    # get normalized sensors readings (range [0, 1]) and apply multiplier
    reads = [(s, s.read(normalize=True)) for s in body.sensors]
    reads = [(k, v * thalamus.multiplier.get(k, 0.0)) for k, v in reads]

    # adapt to range [0-10] and filter non used sensors
    reads = [(k, adapt(v, out_range=cortex.working_range)) for k, v in reads]
    reads = [(sensors[k], v) for k, v in reads if k in sensors]

    # define the pin-resistance/load pairs for the motors
    loads = [(pin, pyramid.sensitivity) for pin in nodes(motors)]

    # stimulate the network with the sensors inputs
    stimulate(network, datasheet, body.run_frequency.s, reads, loads, set())

    # extract outputs from network and remap output values from 0, 10 to:
    #   -6.28, 6.28 for distance: 10 = far -> 6.28 = move straight
    #   6.28, -6.28 for proximity: 10 = near -> -6.28 = go away
    outs = [(motor, network.nodes[pin]['V']) for motor, pin in motors.items()]
    outs = {k: adapt(v, in_range=cortex.working_range) for k, v in outs}

    # set the motors' speed according to its response
    for motor, value in zip(body.motors, map(outs.get, body.motors)):
        motor.speed = adapt(value, out_range=Motor.range(reverse=True))

    # return data for reference
    return dict(zip(sensors.keys(), dict(reads).values())), outs


def describe(robot: Robot) -> str:
    """Return a custom string representation of the object."""

    return ', '.join([
        cortex2str(robot.cortex),
        pyramid2str(robot.pyramid),
        thalamus2str(robot.thalamus)
    ])
