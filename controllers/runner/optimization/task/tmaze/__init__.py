from optimization.task.Task import Task
from optimization.task.tmaze.fitness import Fitness
from optimization.task.tmaze.simulations import live

sensors = tuple([f'gs{_}' for _ in range(1)] + [f'ps{_}' for _ in [0, 7]])

task_description = Task(live, Fitness, sensors)
