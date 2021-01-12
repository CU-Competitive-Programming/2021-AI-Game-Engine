class GameRound(object):

    def __init__(self, players, np_random):
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

    def proceed_round(self, round_number):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of UnoPlayer
            action (str): string of legal action
        '''

        for player in self.players:  # send part 1
            player.send_round_start(round_number)

        for player in self.players:  # send part 1
            player.send_part_start(round_number, "attack")