from enum import Enum


class Colors(Enum):
    """
    Definition of simulation colors perceived by ground sensor.
    Those are discrete levels of a wider grayscale range.
    """

    NONE = -1
    WHITE = 600
    GRAY = 400
    BLACK = 300

    def __eq__(self, other):
        other_value = other.value if isinstance(other, Colors) else other
        return other_value - 50 < self.value < other_value + 50

    def __ge__(self, other):
        other_value = other.value if isinstance(other, Colors) else other
        return self.value >= other_value - 50

    def __le__(self, other):
        other_value = other.value if isinstance(other, Colors) else other
        return self.value <= other_value + 50
