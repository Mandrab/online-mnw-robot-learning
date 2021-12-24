from enum import Enum
from numbers import Number
from typing import Any


class Colors(Enum):
    """
    Definition of simulation colors perceived by ground sensor.
    Those are discrete levels of a wider grayscale range.
    """

    NONE = -1
    WHITE = 825
    GRAY = 625
    BLACK = 325

    @staticmethod
    def convert(value: Number) -> Enum:
        """Map a value to discrete colors."""

        if Colors.WHITE <= value:
            return Colors.WHITE
        elif Colors.BLACK >= value:
            return Colors.BLACK
        return Colors.GRAY

    def __eq__(self, other: Any) -> bool:
        other_value = other.value if isinstance(other, Colors) else other
        return other_value - 50 < self.value < other_value + 50

    def __ge__(self, other: Any) -> bool:
        other_value = other.value if isinstance(other, Colors) else other
        return self.value >= other_value - 50

    def __le__(self, other: Any) -> bool:
        other_value = other.value if isinstance(other, Colors) else other
        return self.value <= other_value + 50
