from optimization.individual import live
from optimization.task.Task import Task
from optimization.task.run.fitness import Fitness

sensors = tuple([f'ps{_}' for _ in range(8)])

task_description = Task(live, Fitness, sensors)
