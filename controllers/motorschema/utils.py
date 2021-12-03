import math
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


def vector_to_length(vector: Tuple[float, float]) -> float:
    x, y = vector
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))


def cartesian_to_polar(vector: Tuple[float, float]) -> Tuple[float, float]:
    x, y = vector
    length = vector_to_length(vector)
    return length, math.atan2(y, x)


def polar_to_cartesian(vector: Tuple[float, float]) -> Tuple[float, float]:
    return reduce(lambda l, a: (l * math.cos(a), l * math.sin(a)), [*vector])


def cartesian_vector_sum(a: Tuple[float, float], b: Tuple[float, float]):
    x1, y1 = a
    x2, y2 = b
    return x1 + x2, y1 + y2


def polar_vector_sum(a: Tuple[float, float], b: Tuple[float, float]):
    a, b = polar_to_cartesian(a), polar_to_cartesian(b)
    return cartesian_to_polar(cartesian_vector_sum(a, b))
