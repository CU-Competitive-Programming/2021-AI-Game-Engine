import json
from copy import deepcopy
from typing import Dict

import numpy as np

from .map import generate_map
from .player import Player
from . import units
from .round import GameRound
import sys


class AIGame(object):
    _units: Dict[int, 'units.Unit']
    _groups: Dict[int, 'units.Group']
    turncount: int = 0
    map: np.array = None
    unit_counter: int = 0
    group_counter: int = 0
    costs: dict = None
    player_id: int = None

    def __init__(self):
        self.np_random = np.random.RandomState()  # This is a random state that will be the basis for our initialization
        self.num_players = len(sys.argv)

    def init_game(self):
        ''' Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        '''
        self.map = generate_map(self.np_random)
        self.players = [Player(self, i, self.np_random, sys.argv[i]) for i in range(self.num_players)]
        self.round = GameRound(self.num_players, self.np_random)

        # Initialize the map for each player
        for player in self.players:
            player.send_init(self.map, self.num_players)

    def step(self):
        ''' Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''

        self.round.proceed_round(self.players)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        state = self.round.get_state(self.players, player_id)
        state['player_num'] = self.num_players
        state['current_player'] = self.round.current_player
        return state

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''
        return self.round.current_player

    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''
        return self.round.is_over

    @property
    def units(self):
        return list(self._units.values())

    @property
    def groups(self):
        return list(self._groups.values())

    def create_unit(self, player, type):
        u = units.Unit(self, self.unit_counter, player, type)
        self.units[self.unit_counter] = u
        self.unit_counter += 1
        return u

    def create_group(self, player, position):
        group = units.Group(self, self.group_counter, player, position)
        self._groups[self.group_counter] = group
        self.group_counter += 1