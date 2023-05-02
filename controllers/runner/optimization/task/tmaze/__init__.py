from optimization.task.task import Task
from optimization.task.tmaze.fitness import Fitness
from optimization.task.tmaze.simulations import live
from robot.body import EPuck
from robot.transducer import IRSensor, GroundSensor

# define the set of sensors needed in the task
sensors = [GroundSensor('gs0')] + [IRSensor(f'ps{_}') for _ in [0, 7]]

task_description = Task(lambda: EPuck.including(sensors), live, Fitness, 15.0, 2.5, 1.5, continuous=False)
