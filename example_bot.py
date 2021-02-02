from library import Bot


class AIBot(Bot):
    def on_attack_start(self):
        for unit in self.myunits:
            if unit.attack_range > 0:
                for enemy in unit.units_within(unit.attack_range, lambda u: u.owner != self.player_id):
                    unit.attack_unit(enemy)
                    break

        self.end_attack()

    def on_move_start(self):
        for unit in self.myunits:
            if unit.collect_amount > 0:
                for position in unit.nearest_nodes():
                    unit.move(position)
                    break
            elif unit.attack_amount > 0:
                for enemy in unit.units_within(unit.attack_range, lambda u: u.owner != self.player_id):
                    unit.move(enemy.position)
                    break

        self.end_move()

    def on_collect_start(self):
        for unit in self.myunits:
            if unit.collect_amount > 0:
                if self.map[unit.position] in (3,4):
                    unit.collect()
                    break

        self.end_collect()

    def on_spawn_start(self):
        for utype, cost in self.costs:
            if all(self.balance[x] - y > 0 for x, y in cost.items()):
                self.create_unit(utype)

        self.end_spawn()


bot = AIBot().run()
