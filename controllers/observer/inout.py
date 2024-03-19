import os

from player.inout import configs
from typing import List, Tuple


OUTPUT_DIRECTORY: str = configs["output"]["path"]
COHESION_FILE: str = configs["output"]["cohesion_file"]
SEPARATION_FILE: str = configs["output"]["separation_file"]


# calculate the cohesion and separation files position
cohesion_path: str = os.path.join(OUTPUT_DIRECTORY, COHESION_FILE)
separation_path: str = os.path.join(OUTPUT_DIRECTORY, SEPARATION_FILE)


def save(data: Tuple[List[float], List[float]]) -> None:
    with open(cohesion_path, "a") as file:
        file.write(", ".join(map(str, data[0])) + "\n")
    with open(separation_path, "a") as file:
        file.write(", ".join(map(str, data[1])) + "\n")
