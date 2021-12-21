import operator

from dataclasses import dataclass
from functools import reduce
from math import copysign
from typing import Tuple


def adapt(
        value: float,
        in_range: Tuple[float, float] = (0.0, 1.0),
        out_range: Tuple[float, float] = (0.0, 1.0)
) -> float:
    """Adapt a value in a range to a different one."""

    in_delta: float = reduce(operator.__sub__, reversed(in_range))
    out_delta: float = reduce(operator.__sub__, reversed(out_range))
    value = (value - min(in_range)) * out_delta / in_delta
    value = out_range[0] + copysign(value, out_delta)

    # force bounds to the value and return it
    return max(min(value, max(out_range)), min(out_range))


@dataclass(frozen=True)
class Frequency:
    """
    Represents the working frequency of the robot.
    Being a class, it avoids usage of different measure units for error.
    """

    hz_value: float

    @property
    def Hz(self) -> float: return self.hz_value

    @property
    def s(self) -> float: return 1.0 / self.Hz

    @property
    def ms(self) -> int: return int(self.s * 1000.0)
