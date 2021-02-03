import json
import time
from copy import deepcopy
from typing import Dict

import numpy as np

from .map import generate_map
from .player import Player
from . import units
from .round import GameRound

from .unit_costs import unit_costs, unit_stats

ROUND_COUNT = 10


class AIGame(object):
    _units: Dict[int, 'units.Unit']
    _groups: Dict[int, 'units.Group']
    turncount: int = 0
    map: np.array = None
    unit_counter: int = 0
    group_counter: int = 0
    costs: dict = None
    player_id: int = None
    players = ()
    round = None
    running = False
    turn = None

    def __init__(self, paths):
        self._units = {}
        self._groups = {}
        self.output = []

        self.np_random = np.random.RandomState()  # This is a random state that will be the basis for our initialization
        self.num_players = len(paths)
        self.players = [Player(self, i, self.np_random, paths[i]) for i in range(self.num_players)]
        self.round = GameRound(self, self.players, self.np_random)

    def run(self):
        self.running = True
        self.init_game()
        for self.turn in range(ROUND_COUNT):
            print(self.turn)
            self.step(self.turn)

        for player in self.players:
            player.send_winner(self.judge_winner())
            player.proc.kill()

        print(self.judge_winner())
        with open(f"output-{time.time()}.json", 'w') as outfile:
            json.dump(self.output, outfile, indent=4)
        self.running = False

    def init_game(self):
        ''' Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        '''
        self.map = generate_map(self.np_random)
        self.costs = unit_costs
        self.unit_stats = unit_stats

        # Initialize the map for each player
        for player in self.players:
            player.send_init(self.map, self.num_players, self.costs)
            player.readthread.start()
            player.errorthread.start()

        print(self.map)

    def step(self, round_number: int):
        ''' Get the next state

            :param round_number: int
        '''

        self.round.proceed_round(round_number)

    @property
    def units(self):
        return list(self._units.values())

    @property
    def groups(self):
        return list(self._groups.values())

    def create_unit(self, player, type):
        u = units.Unit(self, self.unit_counter, player, type, position=player.home, **self.unit_stats[type])
        self._units[self.unit_counter] = u
        self.unit_counter += 1
        return u

    def create_group(self, player, position):
        group = units.Group(self, self.group_counter, player, position)
        self._groups[self.group_counter] = group
        self.group_counter += 1

    def judge_winner(self) -> Player:
        ''' Judge the winner of the game
        Args:
            players (list): The list of players who play the game
        Returns:
            (list): The player id of the winner
        '''
        return max(self.players, key=lambda p: sum(p.balance.values()))

    def get_unit(self, id: int, player: Player = None) -> 'units.Unit':
        unit = self.units[id]
        if unit.owner != player:
            raise RuntimeError(f"Attempted to control unit belonging to other player! {player}, {unit.owner}")

        return unit

    def get_state(self):
        state = {
            'units': [unit.serialize() for unit in self.units],
            'groups': [group.serialize() for group in self.groups],
            'players': {player.player_id: player.balance for player in self.players}
        }
        return state
