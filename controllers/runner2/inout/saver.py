import os

from inout.loader import configs
from nnspy import nns
from simulation.replica import Replica
from typing import Tuple

OUTPUT_DIRECTORY: str = configs["output"]["path"]
PERFORMANCE_FILE: str = configs["output"]["performance_file"]
STATE_FILE: str = configs["output"]["state_file"]
COUPLING_FILE: str = configs["output"]["coupling_file"]

# calculate the performance and state files position
performance_path: str = os.path.join(OUTPUT_DIRECTORY, PERFORMANCE_FILE)
state_path: str = os.path.join(OUTPUT_DIRECTORY, STATE_FILE)
couplings_path: str = os.path.join(OUTPUT_DIRECTORY, COUPLING_FILE)


def save(enumerated_replica: Tuple[int, Replica]):

    index, replica = enumerated_replica

    # write the recorded performance to file
    with open(performance_path, "a") as file:
        performances = [conf.configuration.performance for conf in replica.history]
        file.write(", ".join(map(str, performances)) + "\n")

    # write the recorded states to file
    with open(state_path, "a") as file:
        states = [conf.tsetlin_index for conf in replica.history]
        file.write(", ".join(map(str, states)) + "\n")

    # save the interface used in each simulation epoch
    for idx, it in enumerate([conf.configuration.interface for conf in replica.history]):
        nns.serialize_interface(it.c_interface, OUTPUT_DIRECTORY.encode('utf-8'), index, idx)

        # save the dictionary with the pin and load/multiplier to file
        with open(couplings_path, "a") as file:
            file.write(it.items.__str__() + "\n")

    # save the control information
    ds, nt = replica.network.ds, replica.network.nt
    ns, cc = replica.network.ns, replica.network.cc
    nns.serialize_network(ds, nt, OUTPUT_DIRECTORY.encode('utf-8'), index)
    nns.serialize_state(ds, nt, ns, OUTPUT_DIRECTORY.encode('utf-8'), index, 0)
    nns.serialize_component(cc, OUTPUT_DIRECTORY.encode('utf-8'), index, 0)


__all__ = "save",
