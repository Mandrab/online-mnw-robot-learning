import numpy as np

from controller import Supervisor
from itertools import combinations
from player.inout import configs


COLLISION_RANGE = configs["task"]["collision_range"]
PERCEPTION_RANGE = configs["task"]["perception_range"]
ROBOTS_COUNT = configs["task"]["robots_count"]
TIME_STEP = configs["task"]["time_step_ms"]


supervisor = Supervisor()


def evaluate_step(_):

    # if the webots simulation is paused or stopped, return
    while supervisor.step(TIME_STEP) == -1:
        pass

    # get the position of each robot
    positions = np.array([
        np.array(supervisor.getFromDef(f"Elisa-3_{i + 1}").getPosition())[[0, 2]]
        for i in range(ROBOTS_COUNT)
    ])

    distances = dict()

    # calculate the distance between each robot
    for a, b in combinations(range(ROBOTS_COUNT), 2):
        distance = np.linalg.norm(positions[a] - positions[b])
        distances[a, b] = distances[b, a] = distance

    Cs = np.empty(shape=(ROBOTS_COUNT, 1))
    Ss = np.empty(shape=(ROBOTS_COUNT, 1))

    for a in range(ROBOTS_COUNT):

        # calculate the cohesion factor of each robot: the percentage of robots it is near to

        # find the neighbors of each robot
        neighbors = [b for b in range(ROBOTS_COUNT) if a != b and distances[a, b] < PERCEPTION_RANGE]

        Cs[a] = len(neighbors) / (ROBOTS_COUNT - 1)

        if not neighbors:
            Cs[a] = 0
            Ss[a] = 0
            continue

        # calculate the separation factor of each robot: the percentage of neighbors it touches

        # find pseudo-contacts with other robots
        contacts = [b for b in neighbors if distances[a, b] < COLLISION_RANGE]

        # the performance is inverse to the contacts: the less, the better
        Ss[a] = len(contacts) / ROBOTS_COUNT

    return [Cs.mean(), Ss.mean()]
