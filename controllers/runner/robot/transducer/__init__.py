from controller import Robot
from robot.transducer.sensor import GroundSensor, IRSensor, USSensor
from .sensor import Sensor
from typing import Iterable, Callable


def sensor(name: str) -> Sensor:
    """Get correct sensor according to its name."""
    return IRSensor(name) if name.startswith('ps') else GroundSensor(name)


def enable(robot: Robot) -> Callable[[Sensor], bool]:
    def _(target: Sensor) -> bool:
        target.robot = robot
        if not target.exists():
            return False
        target.enable()
        return True
    return _


def irs(sensors: Iterable[Sensor]) -> Iterable[IRSensor]:
    """Filter IR sensors and return them."""
    return [_ for _ in sensors if isinstance(_, IRSensor)]


def grounds(sensors: Iterable[Sensor]) -> Iterable[GroundSensor]:
    """Filter IR sensors and return them."""
    return [_ for _ in sensors if isinstance(_, GroundSensor)]
