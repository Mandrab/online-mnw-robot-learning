import os

from player.inout import configs
from typing import List, Tuple


OUTPUT_DIRECTORY: str = configs["output"]["path"]
COHESION_FILE: str = configs["output"]["cohesion_file"]
SEPARATION_FILE: str = configs["output"]["separation_file"]
BARYCENTER_FILE: str = configs["output"]["barycenter_file"]
MAP_FILE: str = configs["output"]["map_file"]


# calculate the cohesion and separation files position
cohesion_path: str = os.path.join(OUTPUT_DIRECTORY, COHESION_FILE)
separation_path: str = os.path.join(OUTPUT_DIRECTORY, SEPARATION_FILE)
barycenter_path: str = os.path.join(OUTPUT_DIRECTORY, BARYCENTER_FILE)
map_path: str = os.path.join(OUTPUT_DIRECTORY, MAP_FILE)


def save(data: Tuple[List[float], List[float], List[int], List[int], List[int]]) -> None:
    with open(cohesion_path, "a") as file:
        file.write(", ".join(map(str, data[0])) + "\n")
    with open(separation_path, "a") as file:
        file.write(", ".join(map(str, data[1])) + "\n")
    with open(barycenter_path, "a") as file:
        file.write("x: " + ", ".join(map(str, data[2])) + "\n")
        file.write("y: " + ", ".join(map(str, data[3])) + "\n")
    with open(map_path, "a") as file:
        file.write(", ".join(map(str, data[4])) + "\n")
