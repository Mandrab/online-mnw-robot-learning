import json

from typing import Any, Dict

# open configuration file
with open("../../config.json") as file:
    configs: Dict[str, Any] = json.load(file)

__all__ = "configs",
