from controller import Device, Robot
from inout.loader import configs
from typing import Dict
from webots.supervisor import supervisor

ACTIVE_SENSORS = configs["sensors"]["active"]
ACTIVE_ACTUATORS = configs["actuators"]["active"]
TIME_STEP = configs["task"]["time_step_ms"]

# create an alias for the supervisor
robot = supervisor


def get_sensors(rbt: Robot) -> Dict[str, Device]:
    return dict(zip(ACTIVE_SENSORS, map(rbt.getDevice, ACTIVE_SENSORS)))


def get_actuators(rbt: Robot) -> Dict[str, Device]:
    return dict(zip(ACTIVE_ACTUATORS, map(rbt.getDevice, ACTIVE_ACTUATORS)))


# enable the sensor to work at the specified time step
for _, sensor in get_sensors(robot).items():
    sensor.enable(TIME_STEP)

# set the motor speed to 0
for _, actuator in filter(lambda x: "motor" in x[0], get_actuators(robot).items()):
    actuator.setPosition(float('inf'))
    actuator.setVelocity(0.0)

__all__ = "get_actuators", "get_sensors", "robot"
