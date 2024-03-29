from enum import Enum
from .task import Task
from .avoidance.area import task_description as area_avoidance
from .avoidance.collision import task_description as collision_avoidance
from .run import task_description as run
from .tmaze import task_description as t_maze


class Tasks(Enum):
    """
    Enumeration of implemented tasks to achieve during evolution.
    Each one is associated to a value that contains the epoch logic, the
    functions to crate and update an epoch, the set of sensors used by the
    robot for the task.
    """

    AREA_AVOIDANCE = area_avoidance
    COLLISION_AVOIDANCE = collision_avoidance
    RUN = run
    T_MAZE = t_maze
