from optimization.task.Task import Task
from optimization.task.avoidance.simulations import supplier
from optimization.task.avoidance.area.fitness import Fitness

sensors = tuple([f'gs{_}' for _ in range(1)])
live = supplier(
    [f'area_{index}' for index in range(15)],
    lambda _: min(max(_, -2.5), 2.5)
)

task_description = Task(live, Fitness, sensors)
