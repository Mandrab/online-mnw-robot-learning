from __future__ import annotations
from ctypes import c_int, c_double
from nnspy import interface as nns_interface
from typing import Dict, Tuple, Iterable
from webots.robot import get_actuators, get_sensors, robot

Device, NodeIndex, Multiplier, Load = str, int, float, float


class Interface:

    __internal: Dict[Device, Tuple[NodeIndex, Multiplier]]
    __nns_interface: nns_interface

    def __init__(self, sequence: Iterable[Tuple[str, Tuple[NodeIndex, Multiplier | Load]]]):

        self.__internal = dict(sequence)
        self.__nns_interface = nns_interface()

        actuators_count, sensors_count = len(get_actuators(robot)), len(get_sensors(robot))

        self.__nns_interface.sources_count = sensors_count
        self.__nns_interface.sources_index = (c_int * sensors_count)()
        self.__nns_interface.grounds_count = 0
        self.__nns_interface.grounds_index = (c_int * 0)()
        self.__nns_interface.loads_count = actuators_count
        self.__nns_interface.loads_index = (c_int * actuators_count)()
        self.__nns_interface.loads_weight = (c_double * actuators_count)()

        for key, value in self.__internal.items():

            # if the object is an actuator, change the connection pin
            if key in get_actuators(robot):
                index = list(get_actuators(robot).keys()).index(key)    # TODO
                self.__nns_interface.loads_index[index] = value[0]
                self.__nns_interface.loads_weight[index] = value[1]

            # if the object is a sensor, change the connection pin and its multiplier
            if key in get_sensors(robot):
                index = list(get_sensors(robot).keys()).index(key)  # TODO
                self.__nns_interface.sources_index[index] = value[0]

    def __getitem__(self, key: str) -> Tuple[NodeIndex, Multiplier]:
        return self.__internal[key]

    @property
    def c_interface(self):
        return self.__nns_interface

    @property
    def items(self):
        return self.__internal.items()

    @property
    def multipliers(self) -> Dict[str, float]:
        return {k: v[1] for k, v in self.__internal.items() if v[1] is not None}

    @property
    def pins(self) -> Dict[str, int]:
        return {k: v[0] for k, v in self.__internal.items()}

    def __str__(self):
        return (
            "sources index: " +
            ", ".join(map(str, self.__nns_interface.sources_index[:self.__nns_interface.sources_count])) + "\n" +
            "grounds index: " +
            ", ".join(map(str, self.__nns_interface.grounds_index[:self.__nns_interface.grounds_count])) + "\n" +
            "loads index: " +
            ", ".join(map(str, self.__nns_interface.loads_index[:self.__nns_interface.loads_count])) + "\n" +
            "loads weight: " +
            ", ".join(map(str, self.__nns_interface.loads_weight[:self.__nns_interface.loads_count])) + "\n" +
            self.__internal.__str__()
        )

    def copy(self) -> Interface:
        return Interface(iter(self.__internal.items()))


__all__ = "Interface",
