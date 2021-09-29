import json
import sys
import traceback
from collections import Counter

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
                nearby = list(unit.units_within(unit.attack_range, lambda u: u.owner != self.player_id))
                nearby.sort(key=lambda x: (unit.health <= 0, unit.dist_to(x), -x.collect_amount))

                # print(f"DISTANCES:", [(unit.dist_to(u), -u.collect_amount) for u in nearby], file=sys.stderr)
                if nearby:
                    unit.attack_unit(nearby[0])
                    # print(f"1 ATTACKING UNIT: {nearby[0].collect_amount} {unit.dist_to(nearby[0])}", file=sys.stderr)
                # for enemy in nearby:
                #     print(f"1 ATTACKING UNIT: {unit.collect_amount} {unit.dist_to(enemy)}", file=sys.stderr)
                #     unit.attack_unit(enemy)
                #     break

        self.end_attack()

    def on_move_start(self):
        self.log("move start!")
        # print({u.id: u.collect_amount for u, ass in self.gather_assignments.items()}, file=sys.stderr)
        for unit in self.myunits:
            if unit.collect_amount > 0:
                # print(unit, self.gather_assignments, file=sys.stderr)
                if unit not in self.gather_assignments:
                    self.gather_assignments[unit] = min(self.balance, key=lambda x: self.balance[x])

                for position in unit.nearest_nodes():
                    # print(self.map[tuple(position)], file=sys.stderr)
                    if self.map[tuple(position)] == RESOURCE_TYPES.index(self.gather_assignments[unit]):
                        unit.move(position)
                        break
            elif unit.attack > 0:
                for enemy in sorted(self.enemyunits, key=lambda e: (
                        -e.collect_amount, np.hypot(*(np.array(unit.position) - np.array(e.position))))):
                    # print(f"MOVING TOWARD {enemy.collect_amount} DIST {unit.dist_to(enemy)}", file=sys.stderr)
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

        # print(self.balance, file=sys.stderr)

        ratio = {"gatherer": 1, "attacker": 1}

        counts = Counter(u.type for u in self.myunits)

        while (not self.myunits) or \
                any(ratio[x] / sum(ratio.values()) > counts[x] / sum(counts.values()) for x in counts) or \
                (sum(counts.values()) < 100) or \
                (len(self.myunits) < 2 * len(self.enemyunits)):
            utype = min(
                ratio,
                key=lambda x: ratio[x] / (sum(ratio.values())) <= counts[x] / (sum(counts.values()) or 1)
            )

            if (len(self.myunits) >= 2 * len(self.enemyunits)) and (sum(counts.values()) >= 100):
                break

            if all(self.balance[x] - y >= 0 for x, y in self.costs[utype].items()):
                # print(f"Spawning unit {utype}", file=sys.stderr)
                self.create_unit(utype)
                counts[utype] += 1
            else:
                break

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
