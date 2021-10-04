import copy
from collections import deque, Counter, defaultdict
import numpy as np
from .player import Player

RESOURCE_TYPES = [None, None, None, "wood", "metal"]


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

        self.game.output['turns'].append({})

        for player in self.players:
            for item in player.balance:
                player.balance[item] = player.balance[item] + 1

        for unit in self.game.units:
            unit.attacked_this_round = False
            unit.moved_this_round = False
            unit.collected_this_round = False

        for etype in ["attack", "move", "collect", "spawn"]:
            print("STARTING PART", round_number, etype, len(self.game.units))
            self.game.output['turns'][-1][etype] = copy.deepcopy(self.game.get_state())

            for player in self.players:
                player.send_part_start(round_number, etype)

            Player.get_player_actions(self.players, etype, self.game.turn)

            self.dispatch_actions(etype)

            if etype == "attack":
                dead = []
                for unit in self.game.units:
                    if unit.health <= 0:
                        dead.append(unit)

                for unit in dead:
                    print("Killing unit", unit.owner.player_id, unit.type, unit.id)
                    self.game.remove_unit(unit)

            # if etype == "move":
            #     for unit in self.game.units:
            #         if unit.queued_moves and not unit.moved_this_round:
            #             unit.proceed()
            #
            #     for group in self.game.groups:
            #         if group.queued_moves and not group.moved_this_round:
            #             group.proceed()

    def dispatch_attack(self, actor, target):
        if actor.owner is target.owner:
            raise RuntimeError(f"Can't attack own unit! (Player {actor.owner.player_id})")

        if actor.attacked_this_round:
            raise RuntimeError(f"{actor} has already attacked this round!")

        if np.linalg.norm(np.array(actor.position) - np.array(target.position)) > actor.attack_range:
            raise RuntimeError(f"{actor} attempted to hit out of his range!")
        target.health -= actor.attack
        actor.attacked_this_round = True

    def dispatch_move(self, actor: 'units.Unit', pos: tuple[int, 2]):
        """
        Payload:

        """
        if pos[0] < 0 or pos[1] < 0:
            raise RuntimeError(f"Invalid coordinate pair {pos}")
        if pos[0] >= len(self.game.map[0]) or pos[1] >= len(self.game.map[1]):
            raise RuntimeError(f"Invalid x coordinate {pos[0]}")

        if actor.moved_this_round:
            raise RuntimeError(f"{actor} has already moved this round!")

        actor.move(pos)
        actor.moved_this_round = True

    def dispatch_collect(self, collections, actor):
        if actor.collected_this_round:
            raise RuntimeError(f"{actor} has already collected this round!")

        if collections[tuple(actor.position)]:
            raise RuntimeError(f"{actor.position} has already been collected this round!")
        tile = self.game.map[tuple(actor.position)]
        if tile in (3, 4):  # TODO: Make tiles only harvestable once per turn
            actor.collected_this_round = True
            collections[tuple(actor.position)] = True
            actor.owner.balance[RESOURCE_TYPES[tile]] += actor.collect_amount

            print(f"Giving {actor.owner.player_id} {actor.collect_amount} {RESOURCE_TYPES[tile]} for unit {actor.id}")
        else:
            raise RuntimeError(f"{actor} attempted invalid collect tile {tuple(actor.position)}!")

    def dispatch_spawn(self, player, unit_type):
        print(player, self.game.costs[unit_type])
        if unit_type not in self.game.costs:
            raise RuntimeError(f"{player} attempted to buy invalid unit {unit_type}")

        if any(player.balance.get(cur, 0) < self.game.costs[unit_type][cur] for cur in self.game.costs[unit_type]):
            raise RuntimeError(f"{player} attempted to buy {unit_type} without enough money")

        print(f"Taking {self.game.costs[unit_type]} from {player.player_id}")
        player.balance = {x: player.balance[x] - y for x, y in self.game.costs[unit_type].items()}
        # {x: player.balance[x] - y for x, y in self.game.costs[unit_type].items()}
        self.game.create_unit(player, unit_type)

    def dispatch_actions(self, etype):
        for player in self.players:
            collections = defaultdict(lambda: False)
            while player.action_buffer[self.game.turn][etype]:
                action = player.action_buffer[self.game.turn][etype].popleft()
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
                        self.dispatch_collect(collections, actor)

                    elif etype == "spawn":
                        self.dispatch_spawn(player, action['unit_type'])
