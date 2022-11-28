from optimization.task.task import Task
from optimization.task.avoidance.simulations import supplier
from optimization.task.avoidance.collision.fitness import Fitness
from robot.body import EPuck
from robot.transducer import IRSensor

sensors = [IRSensor(f'ps{_}') for _ in range(8)]
live = supplier([f'box_{_}' for _ in range(20)], lambda _: min(max(_, -.5), .5))

task_description = Task(lambda: EPuck.including(sensors), live, Fitness, 40.0, 5.0, 2.5)
