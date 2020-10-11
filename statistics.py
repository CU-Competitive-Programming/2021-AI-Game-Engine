import json

class PlayerStatistics(object):
	"""Statistics for a player in the game."""
	def __init__(self, arg):
		self.player_id = player_id	# The ID of the player.
		self.random_id = random_id 	# Random number assigned to the player for use in ties.
		self.rank 					# The rank of the player (1 = highest)
		self.last_turn_alive        # The last turn the player remained alive

	def to_json(self):
		# Convert Player statistics to JSON format.
		return json.dumps(self.__dict__)
		
class GameStatistics(object):
	"""Statistics for a game."""
	def __init__(self, arg):
		self.player_statistics       # Statistics for each player.
    	self.number_turns            # Total number of turns that finished before game ends.
    	self.execution_time          # Execution time of the game in ms. 

    def to_json(self):
    	# Convert Game statistics to JSON format.
    	return json.dumps(self.__dict__)

		