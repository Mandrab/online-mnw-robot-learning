from optimization.individual import live
from optimization.task.task import Task
from optimization.task.run.fitness import Fitness

sensors = tuple([f'ps{_}' for _ in range(8)])

task_description = Task(live, Fitness, sensors, 50.0, 0.3, 0.1)
