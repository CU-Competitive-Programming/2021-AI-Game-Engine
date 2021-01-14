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

    def send_state(self):
        """Send the game state to the players"""

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

        for etype in ["attack", "move", "collect", "spawn"]:
            for player in self.players:
                player.send_part_start(round_number, etype)

            Player.get_player_actions(self.players, etype)
            self.dispatch_actions(etype)

    def dispatch_attack(self, actor, target):
        if actor.attacked_this_round:
            raise RuntimeError(f"{actor} has already attacked this round!")
        target.health -= actor.damage
        actor.attacked_this_round = True

    def dispatch_actions(self, etype):
        for player in self.players:
            newactions = deque()
            for action in player.action_buffer:
                if action['command'] == etype:
                    if etype == 'attack':
                        attacker = self.game.get_unit(action['attacker'], player)
                        target = self.game.get_unit(action['target'])

                        self.dispatch_attack(attacker, target)
                else:
                    newactions.append(action)
            player.action_buffer = newactions
