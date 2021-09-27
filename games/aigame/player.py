import json
import os
import queue
import subprocess
import sys
import time
from collections import deque, defaultdict
import select

from games.aigame import units
import socket

import threading

from games.aigame.utils import json_dumps


class Player(object):
    """
    Interaction model:
    - All messages are sent as newline separated JSON. DO NOT PAD/INDENT JSON OR IT WILL BREAK
    - Responses to messages which have a `nonce` will return with that nonce
    - First the map is sent as a json encoded numpy array
    - All actions have a timeout as defined below
    - As players perform their actions, the outputs are sent at the end of the round, and a response to those actions will be awaited
    - Players will have the TIMEOUT window to send their actions for a round.
    - Players can conclude their turn with an action ENDTURN
    - No more nonce, incorrect inputs will be met with a LOSS
    - State is sent back each turn
    """

    ACTION_TIMEOUT = 15  # seconds

    def __init__(self, game, player_id, np_random, file_path):
        ''' Initilize a player.
        Args:
            player_id (int): The id of the player
        '''
        self.game = game
        self.np_random = np_random
        self.player_id = player_id
        self.file_path = file_path
        self.action_buffer = defaultdict(lambda: defaultdict(deque))
        self.error_buffer = ""
        self.balance = {'wood': 15, 'metal': 15}
        self.send_buffer = deque()
        self.home = 0, 0

        if file_path.endswith("py"):
            command = [sys.executable]
        elif file_path.endswith("jar"):
            command = ["java", "-jar"]
        elif file_path.endswith(".out"):
            command = []
        else:
            raise RuntimeError(f"Invalid file type: {file_path}")

        self.proc = subprocess.Popen(
            command + [file_path, '6667'],
            # stdout=subprocess.PIPE,
            # stdin=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            # universal_newlines=True
        )
        (self.sock, address) = self.game.server.accept()

        self.turn_events: dict[dict[str, threading.Event]] = defaultdict(lambda: defaultdict(threading.Event))
        self.readthread = threading.Thread(target=self.handle_input_daemon)
        # self.errorthread = threading.Thread(target=self.handle_error_daemon)

    def handle_input_daemon(self):
        try:
            buffer = b""
            while self.game.running:
                new = self.sock.recv(1024)
                if not new:
                    return
                buffer += new
                while b"\n" in buffer:
                    data, buffer = buffer.split(b"\n", 1)
                    respvalue = json.loads(data)
                    if not respvalue.get("command").startswith("end_"):
                        self.action_buffer[respvalue['turn']][respvalue['part']].append(respvalue)
                    else:
                        self.turn_events[respvalue['turn']][respvalue.get("command").split("_")[1]].set()
        except Exception as e:
            raise RuntimeError(f"Invalid input from player {self.player_id}") from e

    def handle_error_daemon(self):
        while self.game.running:
            r = self.proc.stderr.read(64)
            if not r:
                raise RuntimeError(f"{self} closed pipe")
            print(r.decode(), end="", file=sys.stderr)
            # data = self.proc.stderr.read(64)
            # self.error_buffer += data

    @staticmethod
    def get_player_actions(players: list, eventtype: str, turn: int, timeout: int = 3):
        """Its a staticmethod so it can run for all players at once.
        Send end_move to mark end of move phase early
        """

        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if all(player.turn_events[turn][eventtype].is_set() for player in players):
                print("BREAKING OUT!")
                break
            time.sleep(0.001)

        # print([{**player.turn_events[turn]} for player in players])

        for player in players:
            player.turn_events[eventtype].clear()
        # print(time.monotonic(), end)
        # print(players[0].action_buffer)

    def send_part_start(self, turncount, eventtype):
        gamestate = self.game.get_state()
        resp = dict(type="part_start", turn=turncount, part=eventtype, state=gamestate)

        # if self.sock.closed:
        #     raise RuntimeError("Pipe is closed!")
        self.sock.send(
            json_dumps(resp).encode() + b"\r\n"
        )
        # self.sock.flush()

    def send_winner(self, winner: 'Player'):
        # if self.sock.closed:
        #     raise RuntimeError("Pipe is closed!")

        resp = dict(winners=winner.player_id, type="end_game")

        self.sock.send(
            json_dumps(resp).encode() + b"\r\n"
        )
        # self.sock.flush()

    def send_init(self, map, num_players, costs):
        tmap = map.tolist()
        resp = dict(
            type="initialize",
            map=tmap,
            player_id=self.player_id,
            num_players=num_players,
            balance=self.balance,
            costs=costs
        )

        # if self.sock.closed:
        #     raise RuntimeError("Pipe is closed!")

        self.sock.send(
            json_dumps(resp).encode() + b"\r\n"
        )
        # self.sock.flush()

    # def create_unit(self, type):
    #     """Create a new unit in the game"""
    #     # unit_command = {
    #     #     'command': 'buy',
    #     #     'type': type
    #     # }
    #     if any(self.balance[cur] < self.game.costs[type][cur] for cur in self.game.costs[type]):
    #         raise ValueError("Can't afford to make that unit!")
    #     self.balance -= self.game.costs[type]
    #     return self.game.create_unit(self, type)

    def create_group(self, position):
        """Create a new group for the game"""
        return self.game.create_group(self, position)

    def __str__(self):
        return f"Player({self.player_id}, path='{self.file_path}', bal={self.balance})"

    @property
    def units(self):
        return [unit for unit in self.game.units if unit.owner == self]

    @property
    def groups(self):
        return [group for group in self.game.group if group.owner == self]
