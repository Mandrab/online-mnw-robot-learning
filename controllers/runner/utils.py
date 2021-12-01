import operator

from functools import reduce
from math import copysign
from typing import Tuple


def adapt(
        value: float,
        in_range: Tuple[float, float],
        out_range: Tuple[float, float]
) -> float:
    """Adapt a value to a different range"""

    in_delta: float = reduce(operator.__sub__, reversed(in_range))
    out_delta: float = reduce(operator.__sub__, reversed(out_range))
    value = (value - min(in_range)) * out_delta / in_delta
    value = out_range[0] + copysign(value, out_delta)

    # force bounds to the value
    value = min(value, max(out_range))
    value = max(value, min(out_range))

    return value


class Frequency:
    """
    Represents the working frequency of the robot.
    Being a class, it avoids usage of different measure units for error.
    """
    def __init__(self, hz_value: float):
        self.Hz: float = hz_value
        self.s: float = 1.0 / self.Hz
        self.ms: int = int(self.s * 1000.0)
