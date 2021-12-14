import json
import os
import sys
import time
from contextlib import redirect_stderr
import random
import socket

import numpy as np

from library import units
from library.utils import json_dumps


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
    part = None

    def __init__(self, logging_events=('in', 'out', 'calls')):
        self._units = {}
        self._groups = {}
        self.output = []
        self.player_balances = {}
        self.sock = socket.socket()
        self.sock.connect(('localhost', int(sys.argv[1])))
        self._buffer = b""

        self.logging_events = logging_events

    @property
    def myunits(self):
        return [unit for unit in self.units if unit.owner == self.player_id]

    @property
    def enemyunits(self):
        return [unit for unit in self.units if unit.owner != self.player_id]

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
        pass
        # for item in data:
        #     sys.stderr.write(f"{self.player_id} {os.getpid()} ")
        #     if isinstance(item, (dict, list, tuple)):
        #         self.outfile.write(json.dumps(item) + "\n")
        #         sys.stderr.write(json.dumps(item) + "\n")
        #     else:
        #         self.outfile.write(item + "\n")
        #         sys.stderr.write(item + "\n")
        # sys.stderr.flush()

    def send(self, payload: dict) -> None:
        """Send a payload to the game"""
        payload['turn'] = self.turn
        payload['part'] = self.part
        if not isinstance(payload, str):
            payload = json_dumps(payload)

        self.sock.send(payload.encode() + b"\r\n")
        # self.sock.flush()
        # sys.stderr.write(f"{self.player_id} {os.getpid()} {time.monotonic()}: {payload}\r\n")
        # sys.stderr.flush()
        if 'out' in self.logging_events:
            self.log(payload)

    def recv(self):
        while b"\r\n" not in self._buffer:
            data = self.sock.recv(4096)
            if not data:
                self._buffer += b"\r\n"
            else:
                self._buffer = self._buffer + data
        msg, self._buffer = self._buffer.split(b"\r\n", 1)
        return msg

    def run(self) -> None:
        """
        Run the bot until the game ends
        """
        init = json.loads(self.recv())
        self.on_initialize_raw(init)
        self.outfile = open(f"outfile-{self.player_id}.log", 'w')
        if 'in' in self.logging_events:
            self.log(json.dumps(init))

            self.running = True
            while self.running:
                # event = self.readline()
                event = json.loads(self.recv())
                if 'in' in self.logging_events:
                    self.log(json.dumps(event))
                getattr(self, f"on_{event['type']}_raw")(event)

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
        self._units = {data['id']: units.Unit(bot=self, **data) for data in newstate['units']}
        self._groups = {data['id']: units.Group(bot=self, **data) for data in newstate['groups']}

    def create_unit(self, type):
        #self.log(self.balance, self.costs[type])
        if type not in self.costs:
            raise RuntimeError("Invalid unit type!")
        if any(self.balance.get(cur, 0) < self.costs[type][cur] for cur in self.costs[type]):
            raise RuntimeError(f"Cannot afford to buy unit {type}")

        self.log("BUY BEFORE BALANCE", self.balance)
        for cur, amount in self.costs[type].items():
            self.balance[cur] -= amount

        self.send(dict(command='spawn', unit_type=type))
        self.log("BUY AFTER BALANCE", self.balance)
    #
    # def create_group(self, position):
    #     self.send(dict(command='spawn'))

    def on_part_start_raw(self, payload):
        self.part = payload['part']
        sys.stderr.write(f"{self.player_id} {os.getpid()} {time.time()} STARTING PART {self.part} \r\n")
        sys.stderr.flush()
        self.turn = payload['turn']
        self._update_state(payload['state'])
        getattr(self, f"on_{self.part}_start")()

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