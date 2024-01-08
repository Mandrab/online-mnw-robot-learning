from optimization.task.task import Task
from optimization.task.avoidance.world import supplier
from optimization.task.avoidance.area.fitness import Fitness
from robot.body import EPuck
from robot.transducer import GroundSensor

sensors = [GroundSensor('gs0')]
live = supplier(
    [f'area_{index}' for index in range(15)],
    lambda _: min(max(_, -2.5), 2.5)
)

task_description = Task(lambda: EPuck.including(sensors), live, Fitness, 70.0, 2.5, 1.0)
