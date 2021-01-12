import json
import os
import subprocess
from collections import deque
import select

from games.aigame import units


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
        self.balance = 0
        self.send_buffer = deque()

        if file_path.endswith("py"):
            command = ["python"]
        elif file_path.endswith("jar"):
            command = ["java", "-jar"]
        elif file_path.endswith(".out"):
            command = []
        else:
            raise RuntimeError("Invalid file type!")

        self.proc = subprocess.Popen(
            command + [file_path],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def get_player_actions(self):
        outs, errs = [], []
        while True:
            rr, wr, er = select.select([self.proc.stdout], [], [self.proc.stderr], 0)
            if not rr and not er:
                break
            if rr:
                self.action_buffer.append(json.loads(self.proc.stdout.read(1024)))
            if er:
                self.error_buffer.append(json.loads(self.proc.stderr.read(1024)))

        return outs, errs

    def send_init(self, map, num_players):
        tmap = map.tolist()
        resp = dict(type="init", map=tmap, player_id=self.player_id, num_players=num_players)
        try:
            bouts, berrs = self.proc.communicate(json.dumps(resp).encode(), timeout=self.ACTION_TIMEOUT)
            self.action_buffer.extend(json.loads(x) for x in bouts.decode().split("\n"))
            print(berrs.decode())
        except subprocess.TimeoutExpired:
            pass

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