import os

from control.history import History
from inout.loader import configs
from nnspy import nns

OUTPUT_DIRECTORY: str = configs["output_directory"]
PERFORMANCE_FILE: str = configs["performance_file"]
STATE_FILE: str = configs["state_file"]
COUPLING_FILE: str = configs["coupling_file"]

# calculate the performance and state files position
performance_path: str = os.path.join(OUTPUT_DIRECTORY, PERFORMANCE_FILE)
state_path: str = os.path.join(OUTPUT_DIRECTORY, STATE_FILE)
couplings_path: str = os.path.join(OUTPUT_DIRECTORY, COUPLING_FILE)


def save(data: History):

    # write the recorded performance to file
    with open(performance_path, "a") as file:
        file.write(", ".join(map(str, data.performance_collection)) + "\n")

    # write the recorded states to file
    with open(state_path, "a") as file:
        file.write(", ".join(map(str, data.state_collection)) + "\n")

    # save the interface used in each simulation epoch
    for idx, it in enumerate(data.interface_collection):
        nns.serialize_interface(it, OUTPUT_DIRECTORY.encode('utf-8'), data.controller_index, idx)

        # join the pin and multiplier information for sensory couplings
        couplings = {n: (it.mapping[n], v) for n, v in it.multipliers.items()}

        # create a dictionary with all the information (pin and multiplier for the sensors, pin for the motors) joined
        couplings = it.mapping | couplings

        # save the dictionary to file
        with open(couplings_path, "a") as file:
            file.write(couplings.__str__() + "\n")

    # save the control information
    ds, nt = data.initial_controller.ds, data.initial_controller.nt
    ns, cc = data.initial_controller.ns, data.initial_controller.cc
    nns.serialize_network(ds, nt, OUTPUT_DIRECTORY.encode('utf-8'), data.controller_index)
    nns.serialize_state(ds, nt, ns, OUTPUT_DIRECTORY.encode('utf-8'), data.controller_index, 0)
    nns.serialize_component(cc, OUTPUT_DIRECTORY.encode('utf-8'), data.controller_index, 0)
