from controller import Robot
from typing import Dict, Tuple


class Sensor(str):
    """Represents a robot sensor"""

    # the robot that it is working for/in
    robot: Robot

    # distance sensors lookup table (signal-distance)
    lookup_table: Dict[float, float] = {
        65: 7.0,
        1550: 0.0
    }

    def range(self, raw: bool = True) -> Tuple[float, float]:
        """
        Return range of read values.
        If raw is true: return [min, max] signal's range (i.e. far, near).
        If raw is false: return [min, max] distance's range (i.e. near, far).
        """
        if raw:
            return min(self.lookup_table), max(self.lookup_table)
        return min(self.lookup_table.values()), max(self.lookup_table.values())

    def read(self, raw: bool = True) -> float:
        """
        Returns the sensor reading.
        If raw is true, the function returns the raw signal given by the robot.
        If raw is false, the function returns a distance reading.
        """
        value = self.robot.getDevice(self).getValue()

        # return raw sensor reading
        if raw:
            return value

        # get adapted value directly from the lookup table
        if value in self.lookup_table:
            return self.lookup_table[value]

        # to avoid ranges errors, if the value is out of the raw-range, return
        # the boundaries
        upper_bound = max(self.lookup_table)
        if value > upper_bound:
            return self.lookup_table[upper_bound]
        lower_bound = min(self.lookup_table)
        if value < lower_bound:
            return self.lookup_table[lower_bound]

        # get the nearest values in the table
        lower_bound = max(key for key in self.lookup_table if key < value)
        upper_bound = min(key for key in self.lookup_table if key > value)

        # get the distance value of the raw signals
        lower_value = self.lookup_table[lower_bound]
        upper_value = self.lookup_table[upper_bound]

        # return the average of them
        return (lower_value + upper_value) / 2.0

    def upper_bound(self, raw: bool = True) -> float:
        """Get the max value the device can return"""
        if raw:
            return self.robot.getDevice(self).getMaxValue()
        return max(self.lookup_table.values())

    def lower_bound(self, raw: bool = True) -> float:
        """Get the min value the device can return"""
        if raw:
            return self.robot.getDevice(self).getMinValue()
        return max(self.lookup_table.values())

    def enable(self, update_frequency: int):
        self.robot.getDevice(self).enable(update_frequency)


class Motor(str):
    """Represents a robot motor"""

    # the robot that it is working for/in
    robot: Robot

    @staticmethod
    def range(reverse: bool = False) -> Tuple[float, float]:
        return (6.28, -6.28) if reverse else (-6.28, 6.28)

    @property
    def speed(self) -> float:
        return self.robot.getDevice(self).getVelocity()

    @speed.setter
    def speed(self, value: float):
        self.robot.getDevice(self).setPosition(float('inf'))
        self.robot.getDevice(self).setVelocity(value)
