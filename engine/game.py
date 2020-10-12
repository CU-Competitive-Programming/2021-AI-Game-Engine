from dataclasses import field, dataclass
from typing import List

from engine import unit


@dataclass(init=True, repr=True)
class Game:
    units: List['unit.Unit'] = field(default_factory=list)
    groups: List['unit.Group'] = field(default_factory=list)

    def create_unit(self, *args):  # give actual arguments at some point
        """Create a new unit in the game"""
        u = unit.Unit(self, len(self.units), *args)
        self.units.append(u)
        return u

    def create_group(self, *args):
        """Create a new group for the game"""
        group = unit.Group(self, len(self.groups), *args)
        self.groups.append(group)
        return group
