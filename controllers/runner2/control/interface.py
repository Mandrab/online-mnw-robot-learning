from nnspy import interface, nns
from typing import Dict


class Interface(interface):

    mapping: Dict[str, int]
    multipliers: Dict[str, float]

    def __str__(self):
        return "sources index: " + ", ".join(map(str, self.sources_index[:self.sources_count])) + "\n" + \
            "grounds index: " + ", ".join(map(str, self.grounds_index[:self.grounds_count])) + "\n" + \
            "loads index: " + ", ".join(map(str, self.loads_index[:self.loads_count])) + "\n" + \
            "loads weight: " + ", ".join(map(str, self.loads_weight[:self.loads_count])) + "\n" + \
            "mapping: " + self.mapping.__str__() + "\n" + \
            "multipliers: " + self.multipliers.__str__()

    def copy(self):
        new = nns.copy_interface(self)
        return Interface(
            sources_count=new.sources_count, sources_index=new.sources_index,
            grounds_count=new.grounds_count, grounds_index=new.grounds_index,
            loads_count=new.loads_count, loads_index=new.loads_index, loads_weight=new.loads_weight,
            mapping=self.mapping.copy(), multipliers=self.multipliers.copy()
        )
