import json
import sys
import traceback

import numpy as np

from library import Bot

RESOURCE_TYPES = [None, None, None, "wood", "metal"]

class AIBot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gather_assignments = {}

    def on_attack_start(self):
        self.log("attack start!")
        for unit in self.myunits:
            if unit.attack_range > 0:
                nearby = sorted(unit.units_within(unit.attack_range, lambda u: u.owner != self.player_id), key=unit.dist_to)
                for enemy in nearby:
                    unit.attack_unit(enemy)
                    break

        self.end_attack()

    def on_move_start(self):
        self.log("move start!")
        for unit in self.myunits:
            if unit.collect_amount > 0:
                # print(unit, self.gather_assignments, file=sys.stderr)
                if unit not in self.gather_assignments:
                    self.gather_assignments[unit] = min(self.balance, key=self.balance.get)

                for position in unit.nearest_nodes():
                    # print(self.map[tuple(position)], file=sys.stderr)
                    if self.map[tuple(position)] == RESOURCE_TYPES.index(self.gather_assignments[unit]):
                        unit.move(position)
                        break
            elif unit.attack > 0:
                for enemy in sorted(self.enemyunits, key=lambda e: np.hypot(*(np.array(unit.position) - np.array(e.position)))):
                    unit.move(enemy.position)
                    break

        self.end_move()

    def on_collect_start(self):
        self.log("collect start!", len(self.units))
        for unit in self.myunits:
            if unit.collect_amount > 0:
                if self.map[tuple(unit.position)] in (3, 4):
                    unit.collect()

        self.end_collect()

    def on_spawn_start(self):
        # self.log("spawn start!")
        # self.log(self.costs)

        print(self.balance, file=sys.stderr)

        for utype, cost in self.costs.items():
            if all(self.balance[x] - y >= 0 for x, y in cost.items()):
                print(f"Spawning unit {utype}", file=sys.stderr)
                self.create_unit(utype)

        self.end_spawn()

# try:
#     aib = AIBot(logging_events=('in', 'out'))
#     aib.run()
# except Exception as e:
#     open(f'asdasd-{aib.player_id}.out', 'w').write(str(e))

try:
    bot = AIBot(logging_events=('in', 'out'))
    bot.run()
except Exception:
    traceback.print_exc()
finally:
    bot.sock.close()