from dataclasses import dataclass, field
from typing import *

import numpy as np


@dataclass(init=True, repr=True)
class Game:
    units: list['Unit'] = field(default_factory=list)
    groups: list['Group'] = field(default_factory=list)

    def create_unit(self, *args):
        unit = Unit(self, len(self.units), *args)
        self.units.append(unit)
        return unit

    def create_group(self, *args):
        group = Group(self, len(self.groups), *args)
        self.groups.append(group)
        return group


@dataclass(init=True, repr=True, eq=True)
class Unit:  # use dataclass?
    """A base class for all units on the field"""
    game: Game
    id: int
    owner: int  # owner_id
    speed: int
    health: int
    attack: int
    defense: int
    view_range: int
    attack_range: int
    position: np.ndarray  # size 2, alternatively 2-tuple

    queued_moves: List[np.ndarray] = field(default_factory=list)
    _group: 'Group' = field(default=None)

    def move(self, npos) -> None:
        assert len(npos) == 2, "New position must be length 2!"
        if self._group is not None:
            self._group.remove_member(self)

        npos = np.array(npos)
        diff = npos - self.position
        dist = np.hypot(*diff)
        if dist > self.speed:
            diff = self.speed / dist * diff
            self.queued_moves.append(npos)

        self.position = (self.position + diff).astype(int)

    def process_turn(self) -> None:
        if self.queued_moves:
            self.move(self.queued_moves.pop())

    def units_within(self, dist):
        for unit in self.game.units:
            if unit != self:
                if np.hypot(*(unit.position - self.position)) <= dist:
                    yield unit

        for group in self.game.groups:
            if group != self:
                if np.hypot(*(group.position - self.position)) <= dist:
                    yield group


@dataclass(init=True, repr=True, eq=True)
class Group:
    """A group of units"""
    game: Game
    id: int
    position: np.ndarray  # size 2 - alternatively 2-tuple

    queued_moves: List[np.ndarray] = field(default_factory=list)

    members: List[Unit] = field(default_factory=list)

    @property
    def size(self):
        return len(self.members)

    @property
    def attack(self):
        return sum(unit.attack for unit in self.members)

    @property
    def defense(self):
        return sum(unit.defense for unit in self.members)

    @property
    def speed(self):
        return min(self.members, key=lambda unit: unit.speed).speed

    def move(self, npos):
        assert len(npos) == 2, "New position must be length 2!"

        npos = np.array(npos)
        diff = npos - self.position
        dist = np.hypot(*diff)
        if dist > self.speed:
            diff = self.speed / dist * diff
            self.queued_moves.insert(0, npos)

        for unit in self.members:
            unit.move((npos + diff).astype(int))

    def process_turn(self) -> None:
        if self.queued_moves:
            self.move(self.queued_moves.pop())

    def add_member(self, unit: Unit) -> None:
        assert np.hypot(*(unit.position - self.position)) < unit.speed, "Group too far away!"
        unit.position = self.position
        self.members.append(unit)
        unit._group = self

    def remove_member(self, unit: Unit) -> None:
        self.members.remove(unit)
        unit._group = None

    def units_within(self, dist):
        for unit in self.game.units:
            if unit != self:
                if np.hypot(*(unit.position - self.position)) <= dist:
                    yield unit

    def groups_within(self, dist):
        for group in self.game.groups:
            if group != self:
                if np.hypot(*(group.position - self.position)) <= dist:
                    yield group
