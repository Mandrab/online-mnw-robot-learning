import random

from ctypes import byref, c_int
from dataclasses import dataclass
from inout.loader import configs
from nnspy import connected_component, datasheet, network_state, network_topology, nns

NETWORK_DENSITY: float = configs["nn_network"]["density"]
PACKAGE_SIZE: int = configs["nn_network"]["package_size"]
WIRES_LENGTH: float = configs["nn_network"]["wires_length"]


@dataclass(frozen=True)
class Network:

    ds: datasheet
    nt: network_topology
    ns: network_state
    cc: connected_component

    def __str__(self):
        return f"Wires count: {self.ds.wires_count}, Junctions count: {self.nt.js_count}"


def random_network(seed: int):

    # create the datasheet of a network with the desired density
    ds = datasheet(
        wires_count=int(NETWORK_DENSITY * PACKAGE_SIZE ** 2 / WIRES_LENGTH ** 2),
        length_mean=WIRES_LENGTH,
        length_std_dev=WIRES_LENGTH * 0.35,
        package_size=PACKAGE_SIZE,
        generation_seed=seed,
    )

    # set the random seed
    random.seed(seed)

    # create the network topology, state and components
    cc_count, n2c = c_int(0), (c_int * ds.wires_count)()
    nt = nns.create_network(ds, n2c, byref(cc_count))
    ns = nns.construe_circuit(ds, nt)
    ccs = nns.split_components(ds, nt, n2c, cc_count)[:cc_count.value]
    cc = max(ccs, key=lambda x: int(x.ws_count))

    return Network(ds, nt, ns, cc)
