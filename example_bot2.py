import json
import random
import sys
import traceback
from collections import Counter, defaultdict

import numpy as np

from library import Bot

RESOURCE_TYPES = [None, None, None, "wood", "metal"]


class AIBot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gather_assignments = {}
        self.node_assignments = {}
        self.enemy_assignments = defaultdict(list)
        self.attack_assignments = {}

    def on_attack_start(self):
        self.log("attack start!")
        for unit in self.myunits:
            if self.attack_assignments.get(unit.id) and \
                    not self.enemy_assignments[self.attack_assignments.get(unit.id)]:
                del self.attack_assignments[unit.id]

            if unit.attack_range > 0:
                nearby = list(unit.units_within(unit.attack_range, lambda u: u.owner != self.player_id))
                nearby.sort(key=lambda x: (unit.health <= 0, unit.dist_to(x), -x.collect_amount))

                # print(f"DISTANCES:", [(unit.dist_to(u), -u.collect_amount) for u in nearby], file=sys.stderr)
                if nearby:
                    unit.attack_unit(nearby[0])
                    if nearby[0].health <= 0 and self.enemy_assignments[nearby[0].id]:
                        del self.enemy_assignments[nearby[0].id]
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
                if unit.id not in self.gather_assignments:
                    self.gather_assignments[unit.id] = [min(self.balance, key=lambda x: sum(1 for res,_ in self.gather_assignments.values() if x == res)), None]

                if self.gather_assignments[unit.id][1]:
                    unit.move(self.gather_assignments[unit.id][1])
                    continue

                for position in unit.nearest_nodes():
                    # print(self.map[tuple(position)], file=sys.stderr)
                    if tuple(position) not in self.node_assignments and \
                            self.map[tuple(position)] == RESOURCE_TYPES.index(self.gather_assignments[unit.id][0]):
                        unit.move(position)
                        self.node_assignments[tuple(position)] = unit.id
                        self.gather_assignments[unit.id][1] = tuple(position)
                        break
            elif unit.attack > 0:
                target = self.attack_assignments.get(unit.id)
                if target and target not in self._units:
                    del self.attack_assignments[unit.id]
                    target = None

                if target:
                    print('t', self._units[target].position, file=sys.stderr)
                    unit.move(self._units[target].position)
                else:
                    for enemy in sorted(self.enemyunits, key=lambda e: (
                            -e.collect_amount, np.hypot(*(np.array(unit.position) - np.array(e.position))))):
                        # print(f"MOVING TOWARD {enemy.collect_amount} DIST {unit.dist_to(enemy)}", file=sys.stderr)
                        if len(self.enemy_assignments[enemy.id]) == 3:
                            continue
                        else:
                            self.enemy_assignments[enemy.id].append(unit.id)
                            self.attack_assignments[unit.id] = enemy.id

                        unit.move(enemy.position)
                        break

        self.end_move()

    def on_collect_start(self):
        self.log("collect start!", len(self.units))
        for unit in self.myunits:
            if unit.collect_amount > 0:
                if self.map[tuple(unit.position)] in (3, 4):
                    print(f"Collecting unit {unit.id}", file=sys.stderr)
                    unit.collect()

        self.end_collect()


    ratio = {"gatherer": random.randint(1,3), "attacker": random.randint(1,3)}
    def on_spawn_start(self):
        if self.turn == 0:
            self.create_unit('gatherer')
            self.create_unit('gatherer')

        # self.log("spawn start!")
        # self.log(self.costs)

        # print(self.balance, file=sys.stderr)
        ratio = self.ratio

        counts = Counter(u.type for u in self.myunits)

        while (not self.myunits) or \
                any(ratio[x] / sum(ratio.values()) > counts[x] / sum(counts.values()) for x in counts) or \
                (sum(counts.values()) < 100) or \
                (len(self.myunits) < 2 * len(self.enemyunits)):
            if self.myunits and counts['gatherer'] >= len(list(self.myunits[0].nearest_nodes())):
                utype = min(
                    {'attacker': 1},
                    key=lambda x: ratio[x] / (sum(ratio.values())) <= counts[x] / (sum(counts.values()) or 1)
                )
            else:
                utype = min(
                    ratio,
                    key=lambda x: ratio[x] / (sum(ratio.values())) <= counts[x] / (sum(counts.values()) or 1)
                )

            if (len(self.myunits) >= 2 * len(self.enemyunits)) and (sum(counts.values()) >= 100):
                break

            if all(self.balance[x] >= y for x, y in self.costs[utype].items()):
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
