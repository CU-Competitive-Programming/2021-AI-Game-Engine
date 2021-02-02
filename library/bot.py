import json
import numpy as np

from library import units

init = json.loads(input())


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

    def __init__(self, do_logging=True):
        self._units = {}
        self._groups = {}
        self.output = []
        self.player_balances = {}

        self.do_logging = do_logging
        if do_logging:
            self.outfile = open(f"outfile-{init['player_id']}.log", 'a')

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

    def send(self, payload: dict) -> None:
        """Send a payload to the game"""
        if not isinstance(payload, str):
            payload = json.dumps(payload)

        print(payload)
        self.outfile.write(payload + "\n")

    def run(self) -> None:
        """
        Run the bot until the game ends
        """
        self.running = True
        while self.running:
            event = json.loads(input())
            getattr(self, f"on_{event['initialize']}_raw")(event)

        if self.do_logging:
            self.outfile.close()

    def on_init_raw(self, payload):
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
        self._units = [units.Unit(**data) for data in newstate['units']]
        self._groups = [units.Group(**data) for data in newstate['groups']]

    def create_unit(self, type):
        if type not in self.costs:
            raise RuntimeError("Invalid unit type!")
        if any(self.balance[cur] > self.costs[type][cur] for cur in self.costs[type]):
            raise RuntimeError(f"Cannot afford to buy unit {type}")
        self.send(dict(command='spawn', unit_type=type))
    #
    # def create_group(self, position):
    #     self.send(dict(command='spawn'))

    def on_part_start_raw(self, payload):
        part = payload['part']
        self.turn = payload['turncount']
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