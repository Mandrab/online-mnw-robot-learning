from functools import reduce
from nnspy import connected_component
from typing import Set, Tuple


def minimum_distance_selection(
        component: connected_component,
        outputs: Set[int],
        distance: int,
        negate: bool = False
) -> Set[int]:
    """
    Select nodes 'distance' step distant from the outputs (i.e. loads and grounds).
    If 'negate' is True, the function is `negated` and the returned nodes are the
    grounds, outputs and their neighbors. The nodes have to be numbered according to the
    connected component index, e.g.: node 10 in the NN may be the node 1 in the CC.
    The returned legal nodes are indexed according to the connected component.
    """

    # get the index of connected nodes
    def decompose(idx: int) -> Tuple[int, int]: return idx / component.ws_count, idx % component.ws_count
    coupled_nodes = component.Is[:component.js_count]
    coupled_nodes = map(decompose, coupled_nodes)

    # find the nodes nearer than 'distance' steps from the starting nodes
    def neighbours(group: Set[int], decreased_distance: int) -> Set[int]:

        # base condition: distance 0 is empty set
        if decreased_distance <= 0:
            return group

        # add the nodes adjacent to the group (i.e., the neighbours) to the group itself
        group = reduce(
            lambda s, p:
                s | {p[0], p[1]}                    # if these nodes are connected with the group (i.e., if one of
                if p[0] in group or p[1] in group   # them is part of the group), they are part of the neighborhood
                else s,                             # if these nodes are not connected with the group, skip them
            coupled_nodes,                          # we consider all the junctions of the NN
            group
        )

        return neighbours(group, decreased_distance - 1)

    # find the 'distance' step neighbors to the outputs
    neighbors = neighbours(outputs, distance)

    # returns the neighbor nodes
    if negate:
        return neighbors

    # remove ground and load nodes from the viable ones
    viable_nodes = range(component.ws_count)
    viable_nodes = set(viable_nodes) - neighbors

    return viable_nodes
