import operator

from functools import reduce
from typing import Tuple


def adapt(
        value: float,
        in_range: Tuple[float, float],
        out_range: Tuple[float, float]
) -> float:
    """Adapt a value to a different range"""

    in_delta = reduce(operator.__sub__, reversed(in_range))
    out_delta = reduce(operator.__sub__, reversed(out_range))
    value = out_range[0] + (value - in_range[0]) * out_delta / in_delta

    # force bounds to the value
    value = min(value, out_range[1])
    value = max(value, out_range[0])

    return value
