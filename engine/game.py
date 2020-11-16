import json
import traceback
from dataclasses import field, dataclass
from typing import List, Dict
import numpy as np

from engine import unit

sample_turn_data = {
    'units': [
        {
            'type': 0,
            'owner': 1,
            'position': [46, 32],
            'health': 20,
            'id': 0
        }
    ],
    'turn': 5,
    'balance': 50
}

sample_start_data = {
    'map': [  # See enums.Terrain for terrain designations
        []
    ]
}


@dataclass(init=True, repr=True)
class Game:
    _units: Dict[int, 'unit.Unit'] = field(default_factory=list)
    _groups: Dict[int, 'unit.Group'] = field(default_factory=list)
    turncount: int = 0
    map: np.array = None
    unit_counter: int = 0
    group_counter: int = 0
    costs: dict = None
    player_id: int = None

    @property
    def units(self):
        return list(self._units.values())

    @property
    def groups(self):
        return list(self._groups.values())

    def create_unit(self, type):
        """Create a new unit in the game"""
        unit_command = {
            'command': 'buy',
            'type': type
        }
        self.balance -= self.costs[type]
        print(json.dumps(unit_command))
        # u = unit.Unit(self, self.unit_counter, *args)
        # self.units[self.unit_counter] = u
        # self.unit_counter += 1
        # return u

    def create_group(self, position):
        """Create a new group for the game"""
        group = unit.Group(self, self.group_counter, self.player_id, position)
        self._groups[self.group_counter] = group
        self.group_counter += 1
        return group

    def on_error(self, error):
        print(error)

    def dispatch(self, command, *args, **kwargs):
        try:
            getattr(self, 'on_' + command)(*args, **kwargs)
        except Exception as e:
            try:
                self.on_error(e)
            except:
                traceback.print_exc()

    def run(self):
        start_data = json.loads(input())
        self.costs = {int(k): v for k, v in start_data['costs'].items()}
        self.player_id = start_data["player_id"]

        while True:
            turndata = json.loads(input())
            self.turncount = turndata["turn"]
            self.balance = turndata['balance']

            cunits = set()
            for unitdata in turndata['units']:
                if self._units.get(unitdata['id']) is None:
                    self._units[unitdata['id']] = unit.Unit(self, unitdata['id'], unitdata['owner'], )  # TODO: Add args
                    self.dispatch('unit_create', unit)
                cunits.add(unitdata['id'])

            for deadunit in set(self._units.keys()) - cunits:
                self.dispatch('unit_destroyed', self._units.pop(deadunit))

    def on_unit_created(self, unit):
        pass

    def on_unit_destroyed(self, unit):
        pass
