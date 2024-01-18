from inout.loader import configs
from task.collision_avoidance.step import step as collision_avoidance_step
from task.foraging.step import step as foraging_step
from task.tmaze.step import step as tmaze_step

TASK_TYPE = configs["task"]["type"]

if TASK_TYPE == "COLLISION_AVOIDANCE":
    step = collision_avoidance_step
if TASK_TYPE == "FORAGING":
    step = foraging_step
if TASK_TYPE == "T-MAZE":
    step = tmaze_step

__all__ = "step",
