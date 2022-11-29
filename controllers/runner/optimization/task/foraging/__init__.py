from math import atan2, cos, isclose, sin
from optimization.task.task import Task
from optimization.task.foraging.fitness import Fitness
from optimization.task.foraging.simulations import live
from robot.body import EPuck
from robot.transducer import GroundSensor, IRSensor
from robot.transducer.motor import Motor
from robot.transducer.transducer import Transducer
from typing import Tuple, Any


def _facing(robot, obj) -> bool:
    """Check if the object is in front of the robot."""

    if obj.getNumberOfContactPoints() == 0:
        return False

    # get the robot position and direction
    robot_x, _, robot_y = robot.getFromDef('evolvable').getPosition()
    _, multiplier, _, robot_angle = robot.getFromDef('evolvable').getField('rotation').getSFRotation()
    robot_angle = multiplier * robot_angle

    # get obj contact point and calculate its angle/direction referred to the robot center
    contact_x, _, contact_y = obj.getContactPoint(0)
    contact_angle = atan2(robot_x - contact_x, robot_y - contact_y)

    # calculate the cos and sin of the robot direction and collision point
    cr, sr = cos(robot_angle), sin(robot_angle)
    cc, sc = cos(contact_angle), sin(contact_angle)

    # calculate if the robot faces an object on its north, east, sud, west
    ns_facing = isclose(cc, cr, abs_tol=0.5) and sr * sc > 0
    we_facing = isclose(sc, sr, abs_tol=0.5) and cr * cc > 0

    return ns_facing or we_facing


class PreySensor(Transducer[bool]):
    """Perceive a catchable object in front of the robot."""

    def range(self, reverse: bool = False) -> Tuple[bool, bool]: return (True, False) if reverse else (False, True)

    @property
    def value(self) -> bool:
        # find the catchable objects (hardcoded)
        objects = [self._robot.getFromDef(f'box{i}') for i in range(6)]

        # return the true if any object is faced by the robot, false otherwise
        return next(filter(bool, map(lambda _: _facing(self._robot, _), objects)), False)

    @property
    def normalized_value(self): return 1 if self.value else 0


class Gripper(Transducer[int]):
    """Opens or closes a gripper to possibly catch a catchable object."""

    # state of the robotic gripper. 0 is open, 1 is closed
    _state: int = 0
    _prey: Any = None
    captured: bool = False
    deposited: bool = False

    def range(self, reverse: bool = False) -> Tuple[int, int]:
        return (1, 0) if reverse else (0, 1)

    @property
    def value(self) -> int:
        return self._state

    @value.setter
    def value(self, value: int):
        self.captured = False
        self.deposited = False

        value = round(value)
        if self._state == value:
            return

        # if it closes the grip check if there is something to catch
        if self._state == 0 and value == 1:

            # find the catchable objects (hardcoded)
            objects = [self._robot.getFromDef(f'box{i}') for i in range(6)]

            # get the possibly first element that the robot faces
            obj = next(filter(lambda _: _facing(self._robot, _), objects), None)

            if obj is not None:

                # temporary remove the object from the environment (captured)
                obj.getField('translation').setSFVec3f([0, -100, 0])

                # memorize the capture
                self._prey = obj
                self.captured = True

        # if it opens the grip while it is carrying a catchable
        elif self._state == 1 and value == 0 and self._prey != None:

            # get actual position and free the catchable there
            x, y, z = self._robot.getFromDef('evolvable').getPosition()
            self._prey.getField('translation').setSFVec3f([x + 0.1, y, z + 0.1])

            # forget about the catchable
            self._prey = None
            self.deposited = True

        self._state = value


sensors = [GroundSensor('gs0'), PreySensor()] + [IRSensor(f'ps{_}') for _ in range(8)]
motors = [Gripper()] + [Motor(f'{side} wheel motor') for side in ['left', 'right']]

task_description = Task(lambda: EPuck.including(sensors, motors), live, Fitness, 40.0, 5.0, 2.5)
