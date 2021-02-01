from collections import deque

from .player import Player


class GameRound(object):

    def __init__(self, game, players, np_random):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.players = players
        self.np_random = np_random
        self.current_player = 0
        self.num_players = len(players)
        self.is_over = False
        self.winner = None
        self.game = game

    def proceed_round(self, round_number):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of UnoPlayer
            action (str): string of legal action


        Rounds consist of 5 parts
        - Each step send newest game state
        - Get input from user for step
        - Process turn

        attack, move, collect, spawn
        '''

        for unit in self.game.units:
            unit.attacked_this_round = False
            unit.moved_this_round = False
            unit.collected_this_round = False

        for etype in ["attack", "move", "collect", "spawn"]:
            for player in self.players:
                player.send_part_start(round_number, etype)

            Player.get_player_actions(self.players, etype)
            self.dispatch_actions(etype)

            if etype == "move":
                for unit in self.game.units:
                    if unit.queued_moves and not unit.moved_this_round:
                        unit.proceed()

                for group in self.game.groups:
                    if group.queued_moves and not group.moved_this_round:
                        group.proceed()

    def dispatch_attack(self, actor, target):
        if actor.attacked_this_round:
            raise RuntimeError(f"{actor} has already attacked this round!")
        target.health -= actor.damage
        actor.attacked_this_round = True

    @staticmethod
    def raycast(start: tuple[int, 2], end: tuple[int, 2]) -> set[tuple]:
        """
        https://gamedev.stackexchange.com/questions/20103/finding-which-tiles-are-intersected-by-a-line-without-looping-through-all-of-th

        :param start: Start position
        :param end: End position
        :return: List of intersecting tiles
        """
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x = x0
        y = y0
        ns = 1 + dx + dy
        x_inc = 1 if (x1 > x0) else -1
        y_inc = 1 if (y1 > y0) else -1
        dx *= 2
        dy *= 2
        error = dx - dy

        tiles = set()

        for n in range(ns, 0, -1):
            tiles.add((x,y))
            if error > 0:
                x += x_inc
                error -= dy
            elif error < 0:
                y += y_inc
                error += dx
            elif error == 0:
                x += x_inc
                y += y_inc
                error -= dy
                error += dx

        return tiles

    def dispatch_move(self, actor: 'units.Unit', pos: tuple[int, 2]):
        if pos[0] < 0 or pos[1] < 0:
            raise RuntimeError(f"Invalid coordinate pair {pos}")
        if pos[0] >= len(self.game.map[0]) or pos[1] >= len(self.game.map[1]):
            raise RuntimeError(f"Invalid x coordinate {pos[0]}")

        if actor.moved_this_round:
            raise RuntimeError(f"{actor} has already moved this round!")

        for step in self.raycast(actor.position, pos):
            if self.game.map[tuple(step)] == 1:
                raise RuntimeError(f"{actor} attempted invalid move to or through impassable tile {step}")

        actor.move(pos)
        actor.moved_this_round = True

    def dispatch_collect(self, actor):
        if actor.collected_this_round:
            raise RuntimeError(f"{actor} has already collected this round!")

        if self.game.map[tuple(actor.position)] in (3, 4):
            actor.collected_this_round = True
            actor.owner.balance += 0
        else:
            raise RuntimeError(f"{actor} attempted invalid collect tile {tuple(actor.position)}!")

    def dispatch_spawn(self, player, unit_type):
        if unit_type not in self.game.costs:
            raise RuntimeError(f"{player} attempted to buy invalid unit {unit_type}")
        if self.game.costs['unit_type'] > player.balance:
            raise RuntimeError(f"{player} attempted to buy {unit_type} without enough money")

        player.balance -= self.game.costs['unit_type']
        self.game.create_unit(player, unit_type)

    def dispatch_actions(self, etype):
        for player in self.players:
            newactions = deque()
            for action in player.action_buffer:
                if action['command'] == etype:
                    if etype == 'attack':
                        attacker = self.game.get_unit(action['unit'], player)
                        target = self.game.get_unit(action['target'])

                        self.dispatch_attack(attacker, target)
                    elif etype == 'move':
                        actor = self.game.get_unit(action['unit'], player)
                        self.dispatch_move(actor, action['destination'])

                    elif etype == 'collect':
                        actor = self.game.get_unit(action['unit'], player)
                        self.dispatch_collect(actor)

                    elif etype == "spawn":
                        self.dispatch_spawn(player, action['unit_type'])

                else:
                    newactions.append(action)
            player.action_buffer = newactions
