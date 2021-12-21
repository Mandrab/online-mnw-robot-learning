import operator

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

    # force bounds to the value
    return max(min(value, max(out_range)), min(out_range))
