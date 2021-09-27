from collections import deque
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Union

import numpy as np

from . import game, player
from .utils import raycast


@dataclass(init=True, repr=True, eq=True)
class Unit:  # use dataclass?
    """A base class for all units on the field"""
    game: 'game.Game'
    id: int
    owner: 'player.Player'  # owner_id
    type: str
    speed: int
    health: int
    attack: int
    defense: int
    view_range: int
    attack_range: int
    collect_amount: int
    position: np.ndarray  # size 2, alternatively 2-tuple
    attacked_this_round = False
    moved_this_round = False
    collected_this_round = False

    _group: 'Group' = field(default=None)  # This should only be modified from the relevant group object

    def move(self, npos) -> None:  # , new=True
        """Move the unit to a new location. If its further than can be moved this turn, move as far as possible and queue the rest of the movement to happen later."""
        assert len(npos) == 2, "New position must be length 2!"
        # if new:
        #     self.queued_moves.clear()
        if self._group is not None:
            self._group.remove_member(self)

        npos = np.array(npos)
        diff = npos - self.position
        dist = np.hypot(*diff)
        if dist > self.speed:
            diff = self.speed / dist * diff
            # self.queued_moves.append(npos)

        for step in raycast(self.position, self.position + diff):
            if self.game.map[tuple(step)] == 1:
                raise RuntimeError(f"{self} attempted invalid move to or through impassable tile {self}")

        self.position = (self.position + diff).astype(int)

    # NOTE: Code moved to client side
    # queued_moves: List[np.ndarray] = field(default_factory=deque)
    #
    # def proceed(self) -> None:
    #     """If the unit has queued moves, perform the first queued move."""
    #     if self.queued_moves:
    #         self.move(self.queued_moves.pop(), new=False)

    def units_within(self, dist: float, check: Optional[Callable[['Unit'], bool]] = None) -> List['Unit']:
        """Get a list of all units within the given distance of the unit.
        Optionally pass a check function and only return units which pass the check."""
        for unit in self.game.units:
            if ((unit != self) and check(unit)) if check else True:
                if np.hypot(*(np.array(unit.position) - np.array(self.position))) <= dist:
                    yield unit

    def groups_within(self, dist: float, check: Optional[Callable[['Group'], bool]] = None) -> List['Group']:
        """Get a list of all groups within the given distance of the unit.
        Optionally pass a check function and only return groups which pass the check."""
        for group in self.game.groups:
            if group != self and check(group) if check else True:
                if np.hypot(*(group.position - self.position)) <= dist:
                    yield group

    def serialize(self):
        """Return a JSON representable instance of the unit"""
        return dict(
            id=self.id,
            owner=self.owner.player_id,
            type=self.type,
            speed=self.speed,
            health=self.health,
            attack=self.attack,
            defense=self.defense,
            attack_range=self.attack_range,
            view_range=self.view_range,
            collect_amount=self.collect_amount,
            position=list(self.position)
        )


class Gatherer(Unit):
    name = 'gatherer'
    pass


class WeakRanger(Unit):
    name = 'weakranger'
    pass


class StrongRanger(Unit):
    pass


class WeakMelee(Unit):
    pass


class StrongMelee(Unit):
    pass


@dataclass(init=True, repr=True, eq=True)
class Group:
    """A group of units"""
    game: 'game.Game'
    id: int
    owner: 'player.Player'
    position: np.ndarray  # size 2 - alternatively 2-tuple

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
        return min(self.members, key=lambda unit: unit.speed).speed if self.members else 1000000

    def move(self, npos, new=True) -> None:
        """Moves the group and all units in it to the specified location.
         If its further than can be moved this turn, move as far as possible and queue the rest of the movement to happen later."""
        assert len(npos) == 2, "New position must be length 2!"
        # if new:  # clear moves if its a new command
        #     self.queued_moves.clear()

        npos = np.array(npos)
        diff = npos - self.position
        dist = np.hypot(*diff)
        if dist > self.speed:
            diff = self.speed / dist * diff

        for step in raycast(self.position, self.position + diff):
            if self.game.map[tuple(step)] == 1:
                raise RuntimeError(f"{self} attempted invalid move to or through impassable tile {self}")

        for unit in self.members:
            unit.move((npos + diff).astype(int))

    # NOTE: Code moved to client
    # queued_moves: List[np.ndarray] = field(default_factory=list)
    #
    # def proceed(self) -> None:
    #     """If the unit has queued moves, perform the first queued move."""
    #     if self.queued_moves:
    #         self.move(self.queued_moves.pop(), new=False)

    def add_member(self, unit: Unit) -> None:
        """Add a member to the group"""
        assert np.hypot(*(unit.position - self.position)) < unit.speed, "Group too far away!"
        assert unit.owner == self.owner, "The unit must belong to the same player as the group!"
        unit.position = self.position
        self.members.append(unit)
        unit._group = self

    def remove_member(self, unit: Unit) -> None:
        """Remove a member from this group."""
        self.members.remove(unit)
        unit._group = None

    def units_within(self, dist: float, check: Optional[Callable[[Unit], bool]] = None) -> List[Unit]:
        """Get a list of all units within the given distance of the group.
        Optionally pass a check function and only return units which pass the check."""
        for unit in self.game.units:
            if unit != self and check(unit) if check else True:
                if np.hypot(*(np.array(unit.position) - np.array(self.position))) <= dist:
                    yield unit

    def groups_within(self, dist: float, check: Optional[Callable[['Group'], bool]] = None) -> List['Group']:
        """Get a list of all groups within the given distance of the group.
        Optionally pass a check function and only return groups which pass the check."""
        for group in self.game.groups:
            if group != self and check(group) if check else True:
                if np.hypot(*(group.position - self.position)) <= dist:
                    yield group

    def serialize(self):
        """Return a JSON representable instance of the unit"""
        return dict(id=self.id, owner=self.owner.player_id, members=[u.id for u in self.members])
