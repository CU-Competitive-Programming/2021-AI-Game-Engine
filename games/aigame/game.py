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
        self.players = [Player(i, self.np_random, sys.argv[i]) for i in range(self.num_players)]
        self.round = GameRound(self.num_players, self.np_random)

        # Deal 7 cards to each player to prepare for the game
        for player in self.players:
            player.send_map(self.map)

    def step(self, action):
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
        state['player_num'] = self.get_player_num()
        state['current_player'] = self.round.current_player
        return state

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        winner = self.round.winner
        if winner is not None and len(winner) == 1:
            self.payoffs[winner[0]] = 1
            self.payoffs[1 - winner[0]] = -1
        return self.payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_player_num(self):
        ''' Return the number of players in Limit Texas Hold'em

        Returns:
            (int): The number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_action_num():
        ''' Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 61 actions
        '''
        return 61

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

## For test
# if __name__ == '__main__':
#    #import time
#    #random.seed(0)
#    #start = time.time()
#    game = UnoGame()
#    for _ in range(1):
#        state, button = game.init_game()
#        print(button, state)
#        i = 0
#        while not game.is_over():
#            i += 1
#            legal_actions = game.get_legal_actions()
#            print('legal_actions', legal_actions)
#            action = np.random.choice(legal_actions)
#            print('action', action)
#            print()
#            state, button = game.step(action)
#            print(button, state)
#        print(game.get_payoffs())
#    print('step', i)
