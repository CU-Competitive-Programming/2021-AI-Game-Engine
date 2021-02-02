import json
import sys
from contextlib import redirect_stderr
import random

import numpy as np

from library import units


class Bot:
    """A bot class used to interact at a high level with the game"""
    outfile = None
    running = False
    turn = 0
    map = None
    player_id = None
    num_players = None
    balance = None
    costs = None

    def __init__(self, logging_events=('in', 'out', 'calls')):
        self._units = {}
        self._groups = {}
        self.output = []
        self.player_balances = {}

        self.logging_events = logging_events

    @property
    def myunits(self):
        return [unit for unit in self.units if unit.owner == self.player_id]

    @property
    def mygroups(self):
        return [group for group in self.groups if group.owner == self.player_id]

    @property
    def units(self):
        return list(self._units.values())

    @property
    def groups(self):
        return list(self._groups.values())

    def log(self, *data):
        for item in data:
            if isinstance(item, (dict, list, tuple)):
                self.outfile.write(json.dumps(item) + "\n")
            else:
                self.outfile.write(item + "\n")

    def send(self, payload: dict) -> None:
        """Send a payload to the game"""
        if not isinstance(payload, str):
            payload = json.dumps(payload)

        sys.stdout.write(payload + "\r\n")
        #print(payload)
        if 'out' in self.logging_events:
            self.log(payload)

    def run(self) -> None:
        """
        Run the bot until the game ends
        """
        init = json.loads(input())
        self.on_initialize_raw(init)
        self.outfile = open(f"outfile-{self.player_id}.log", 'w')
        if 'in' in self.logging_events:
            self.log(json.dumps(init))

        with redirect_stderr(self.outfile):
            try:
                self.running = True
                while self.running:
                    # event = self.readline()
                    event = json.loads(input())
                    if 'in' in self.logging_events:
                        self.log(json.dumps(event))
                    getattr(self, f"on_{event['type']}_raw")(event)
            finally:
                self.outfile.close()

    def on_initialize_raw(self, payload):
        self.map = np.array(payload['map'])
        self.player_id = payload['player_id']
        self.num_players = payload['num_players']
        self.balance = payload['balance']
        self.costs = payload['costs']
        self.on_game_initialize()

    def on_game_initialize(self):
        """Run when the initial payload is sent"""

    def _update_state(self, newstate):
        self.balance = newstate['players'][str(self.player_id)]
        self.player_balances = newstate['players']
        self._units = {data['id']: units.Unit(**data) for data in newstate['units']}
        self._groups = {data['id']: units.Group(**data) for data in newstate['groups']}

    def create_unit(self, type):
        #self.log(self.balance, self.costs[type])
        if type not in self.costs:
            raise RuntimeError("Invalid unit type!")
        if any(self.balance[cur] < self.costs[type][cur] for cur in self.costs[type]):
            raise RuntimeError(f"Cannot afford to buy unit {type}")
        self.send(dict(command='spawn', unit_type=type))
    #
    # def create_group(self, position):
    #     self.send(dict(command='spawn'))

    def on_part_start_raw(self, payload):
        part = payload['part']
        self.turn = payload['turn']
        self._update_state(payload['state'])
        getattr(self, f"on_{part}_start")()

    def on_attack_start(self):
        pass

    def on_move_start(self):
        pass

    def on_collect_start(self):
        pass

    def on_spawn_start(self):
        pass

    def on_end_game_raw(self, payload: dict):
        """
        dict(winner=winner.player_id, type="end_game")
        """
        self.running = False
        self.on_game_end(payload['winners'])

    def on_game_end(self, winner_ids):
        """Called when the game ends and a winner is decided"""
        print(f"{winner_ids} won!")

    def end_attack(self):
        self.send(dict(command="end_attack"))

    def end_move(self):
        self.send(dict(command="end_move"))

    def end_spawn(self):
        self.send(dict(command="end_spawn"))

    def end_collect(self):
        self.send(dict(command="end_collect"))