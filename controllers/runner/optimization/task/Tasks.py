from enum import Enum
from optimization.task.avoidance.area.epoch import Epoch as AAEpoch
from optimization.task.avoidance.area.epoch import new_epoch as aa_new
from optimization.task.avoidance.area.epoch import evolve_epoch as aa_evolve
from optimization.task.avoidance.collision.epoch import Epoch as CAEpoch
from optimization.task.avoidance.collision.epoch import new_epoch as ca_new
from optimization.task.avoidance.collision.epoch import evolve_epoch as ca_evolve
from optimization.task.run.epoch import Epoch as REpoch
from optimization.task.run.epoch import new_epoch as r_new
from optimization.task.run.epoch import evolve_epoch as r_evolve
from optimization.task.tmaze.epoch import Epoch as TEpoch
from optimization.task.tmaze.epoch import new_epoch as t_new
from optimization.task.tmaze.epoch import evolve_epoch as t_evolve


class Tasks(Enum):
    """Enumeration of implemented tasks to achieve during evolution."""

    AREA_AVOIDANCE = (AAEpoch, aa_new, aa_evolve)
    COLLISION_AVOIDANCE = (CAEpoch, ca_new, ca_evolve)
    RUN = (REpoch, r_new, r_evolve)
    T_MAZE = (TEpoch, t_new, t_evolve)
