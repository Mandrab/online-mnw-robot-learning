from inout.loader import configs
from task.collision_avoidance.evaluator import evaluate as collision_avoidance_evaluation

TASK_TYPE = configs["task_type"]


if TASK_TYPE == "COLLISION_AVOIDANCE":
    evaluate = collision_avoidance_evaluation

__all__ = "evaluate",
