from dataclasses import dataclass
from ctypes import byref, c_int
from nnspy import connected_component, datasheet, network_state, network_topology, nns
from typing import Tuple


@dataclass(frozen=True)
class Cortex:
    """
    It's a wrapper for the device/controller and represents the reasoning area
    (or 'brain') of the robot. When provided with correct information, it
    creates a graceful interface to the more hardware-oriented logic of the
    device.
    """

    # graphs information and instance
    datasheet: datasheet
    topology: network_topology
    state: network_state
    component: connected_component

    # accepted stimulus range of the network
    working_range: Tuple[float, float] = (0.0, 3.3)


def new(ds: datasheet) -> Cortex:
    """Get a device represented by the given datasheet and initialize it."""

    cc_count, n2c = c_int(0), (c_int * ds.wires_count)()
    nt = nns.create_network(ds, n2c, byref(cc_count))
    ns = nns.construe_circuit(ds, nt)
    ccs = nns.split_components(ds, nt, n2c, cc_count)[:cc_count.value]
    cc = max(ccs, key=lambda x: int(x.ws_count))

    return Cortex(ds, nt, ns, cc)


def describe(instance: Cortex):
    """Return a custom string representation of the object."""

    ds, cc = instance.datasheet, instance.component
    area = ds.package_size ** 2
    d = ds.wires_count * ds.length_mean ** 2 / area

    return str(f'Device density: {d}, CC #wires: {cc.ws_count}, CC #junctions: {cc.js_count}')
