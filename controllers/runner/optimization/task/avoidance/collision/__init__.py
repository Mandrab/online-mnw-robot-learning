from optimization.task.task import Task
from optimization.task.avoidance.simulations import supplier
from optimization.task.avoidance.collision.fitness import Fitness

sensors = tuple([f'ps{_}' for _ in range(8)])
live = supplier([f'box_{_}' for _ in range(20)], lambda _: min(max(_, -.5), .5))

task_description = Task(live, Fitness, sensors, 30.0, 0.3, 0.1)
