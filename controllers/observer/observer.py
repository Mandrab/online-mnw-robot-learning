import numpy as np

from controller import Supervisor
from inout import configs
from itertools import combinations

TIME_STEP = configs["task"]["time_step_ms"]
ROBOTS_COUNT = configs["task"]["robots_count"]
EPOCHS_COUNT = configs["task"]["epochs_count"]
EPOCH_DURATION = configs["task"]["epochs_duration"]

RANGE = 0.15
TOUCH_RANGE = 0.08

supervisor = Supervisor()

for epoch in range(EPOCHS_COUNT):

    Css = list()
    Sss = list()

    for step in range(EPOCH_DURATION):

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
            neighbors = [b for b in range(ROBOTS_COUNT) if a != b and distances[a, b] < RANGE]

            Cs[a] = len(neighbors) / (ROBOTS_COUNT - 1)

            if not neighbors:
                Cs[a] = 0
                Ss[a] = 0
                continue

            # calculate the separation factor of each robot: the percentage of neighbors it touches

            # find pseudo-contacts with other robots
            contacts = [b for b in neighbors if distances[a, b] < TOUCH_RANGE]

            # the performance is inverse to the contacts: the less, the better
            Ss[a] = len(contacts) / ROBOTS_COUNT

        Css.append(Cs.mean())
        Sss.append(Ss.mean())

    with open("cohesion.dat", "a") as file:
        file.write(", ".join(map(str, Css)) + "\n")
    with open("separation.dat", "a") as file:
        file.write(", ".join(map(str, Sss)) + "\n")
