from optimization.task.task import Task
from optimization.task.foraging.fitness import Fitness
from optimization.task.foraging.world import live
from optimization.task.foraging.gripper import Gripper
from optimization.task.foraging.sensor import PreySensor
from robot.body import EPuck
from robot.transducer import GroundSensor, IRSensor
from robot.transducer.motor import Motor
from utils import adapt


class ReverseGroundSensor(GroundSensor):
    """Ground sensor that returns 4095 if the floor is black and 0 if it is white."""

    @property
    def value(self) -> float: return adapt(self._robot.getDevice(self).getValue(), self.range(), self.range(reversed))


sensors = [GroundSensor('gs0'), ReverseGroundSensor('gs2')] + [
    IRSensor(f'ls{_}') for _ in range(8)
]
motors = [Gripper('gripper'), Motor('left wheel motor'), Motor('right wheel motor')]

task_description = Task(lambda: EPuck.including(sensors, motors), live, Fitness, 0.0, 2.0, 2.5)
