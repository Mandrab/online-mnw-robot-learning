from typing import Dict, Iterable

Fiber = Dict[str, int]
"""
A mapping from the cortex to a transducer. It connects the transducer with the
cortex node. The string is the transducer name, while the integer is the network
node.
"""


def transducers(fiber: Fiber) -> Iterable[str]: return fiber.keys()


def nodes(fiber: Fiber) -> Iterable[int]: return fiber.values()
