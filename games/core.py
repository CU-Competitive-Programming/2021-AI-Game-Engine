''' Game-related and Env-related base classes
'''
from dataclasses import dataclass, field
from typing import List, Optional, Callable

import numpy as np


@dataclass(init=True, repr=True, eq=True)
class Unit:
    game: 'Game'
    id: int
    owner: int  # owner_id
    speed: int
    health: int
    attack: int
    defense: int
    view_range: int
    attack_range: int
    position: np.ndarray  # size 2, alternatively 2-tuple


@dataclass(init=True, repr=True, eq=True)
class Group:
    """A group of units"""
    game: 'game.Game'
    id: int
    owner: int
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

    def move(self, npos) -> None:
        raise NotImplementedError

    def process_turn(self) -> None:
        """If the unit has queued moves, perform the first queued move."""
        raise NotImplementedError

    def add_member(self, unit: Unit) -> None:
        """Add a member to the group"""
        raise NotImplementedError

    def remove_member(self, unit: Unit) -> None:
        """Remove a member from this group."""
        self.members.remove(unit)
        unit._group = None

    def units_within(self, dist: float, check: Optional[Callable[[Unit], bool]] = None) -> List[Unit]:
        """Get a list of all units within the given distance of the group.
        Optionally pass a check function and only return units which pass the check."""
        raise NotImplementedError

    def groups_within(self, dist: float, check: Optional[Callable[['Group'], bool]] = None) -> List['Group']:
        """Get a list of all groups within the given distance of the group.
        Optionally pass a check function and only return groups which pass the check."""
        raise NotImplementedError


class Player:
    ''' Player stores cards in the player's hand, and can determine the actions can be made according to the rules
    '''

    player_id = None
    hand = []

    def __init__(self, player_id):
        ''' Every player should have a unique player id
        '''
        self.player_id = player_id

    def available_order(self):
        ''' Get the actions can be made based on the rules
        Returns:
            list: a list of available orders
        '''
        raise NotImplementedError

    def play(self):
        ''' Player's actual action in the round
        '''
        raise NotImplementedError


class Judger(object):
    ''' Judger decides whether the round/game ends and return the winner of the round/game
    '''

    def judge_round(self, **kwargs):
        ''' Decide whether the round ends, and return the winner of the round
        Returns:
            int: return the player's id who wins the round or -1 meaning the round has not ended
        '''
        raise NotImplementedError

    def judge_game(self, **kwargs):
        ''' Decide whether the game ends, and return the winner of the game
        Returns:
            int: return the player's id who wins the game or -1 meaning the game has not ended
        '''
        raise NotImplementedError


class Round(object):
    ''' Round stores the id the ongoing round and can call other Classes' functions to keep the game running
    '''

    def __init__(self):
        ''' When the game starts, round id should be 1
        '''

        raise NotImplementedError

    def proceed_round(self, **kwargs):
        ''' Call other Classes's functions to keep the game running
        '''
        raise NotImplementedError


class Game(object):
    ''' Game class. This class will interact with outer environment.
    '''

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        raise NotImplementedError

    def step(self, action):
        ''' Perform one draw of the game and return next player number, and the state for next player
        '''
        raise NotImplementedError

    def step_back(self):
        ''' Takes one step backward and restore to the last state
        '''
        raise NotImplementedError

    def get_player_num(self):
        ''' Retrun the number of players in the game
        '''
        raise NotImplementedError

    def get_action_num(self):
        ''' Return the number of possible actions in the game
        '''
        raise NotImplementedError

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        raise NotImplementedError

    def is_over(self):
        ''' Return whether the current game is over
        '''
        raise NotImplementedError
