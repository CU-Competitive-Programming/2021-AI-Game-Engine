import json
import os
import subprocess
import time
from collections import deque
import select

from games.aigame import units
import socket


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
        self.action_buffer = deque()
        self.error_buffer = deque()
        self.balance = {'wood': 0, 'metal': 0}
        self.send_buffer = deque()

        if file_path.endswith("py"):
            command = ["python3.8"]
        elif file_path.endswith("jar"):
            command = ["java", "-jar"]
        elif file_path.endswith(".out"):
            command = []
        else:
            raise RuntimeError(f"Invalid file type: {file_path}")

        self.proc = subprocess.Popen(
            command + [file_path],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    @staticmethod
    def get_player_actions(players: list, eventtype: str, timeout: int = 5):
        """Its a staticmethod so it can run for all players at once.
        Send end_move to mark end of move phase early
        """
        player_files = {player.proc.stdout: player for player in players}
        player_errors = {player.proc.stderr: player for player in players}
        end = time.monotonic() + timeout
        while player_files and time.monotonic() < end:
            rr, wr, er = select.select(player_files.keys(), [], player_errors.keys(), 0)  # check input nowait
            if not rr and not er:
                break
            for efile in er:
                player_files[efile].error_buffer.append(json.loads(efile.read(1024)))
            for rfile in rr:
                respvalue = json.loads(rfile.read(1024))
                if respvalue.get("action") != "end_" + eventtype:
                    player_files[rfile].action_buffer.append(respvalue)
                else:
                    del player_files[rfile]
                    del player_errors[rfile]

        print(players[0].action_buffer)

    def send_part_start(self, turncount, eventtype):
        gamestate = self.game.get_state()
        resp = dict(type="part_start", turn=turncount, part=eventtype, state=gamestate)
        self.proc.stdin.write(
            json.dumps(resp).encode()
        )

    def send_init(self, map, num_players):
        tmap = map.tolist()
        resp = dict(type="init", map=tmap, player_id=self.player_id, num_players=num_players)
        self.proc.stdin.write(
            json.dumps(resp).encode()
        )

    def create_unit(self, type):
        """Create a new unit in the game"""
        # unit_command = {
        #     'command': 'buy',
        #     'type': type
        # }
        if self.balance < self.game.costs[type]:
            raise ValueError("Can't afford to make that unit!")
        self.balance -= self.game.costs[type]
        return self.game.create_unit(self, type)

    def create_group(self, position):
        """Create a new group for the game"""
        return self.game.create_group(self, position)

    def __str__(self):
        return f"Player({self.player_id}, path='{self.file_path}')"

    @property
    def units(self):
        return [unit for unit in self.game.units if unit.owner == self]

    @property
    def groups(self):
        return [group for group in self.game.group if group.owner == self]