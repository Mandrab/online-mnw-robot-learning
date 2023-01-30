from optimization.task.task import Task
from optimization.task.connected_coverage.fitness import Fitness
from optimization.task.connected_coverage.simulations import live
from robot.body import EPuck
from robot.transducer.sensor import USSensor
from robot.transducer.motor import Motor


sensors = [USSensor(f'us{_}') for _ in range(8)]
motors = [Motor(f'{side} wheel motor') for side in ['left', 'right']]

task_description = Task(lambda: EPuck.including(sensors, motors), live, Fitness, 20.0, 2.0, 2.5)
