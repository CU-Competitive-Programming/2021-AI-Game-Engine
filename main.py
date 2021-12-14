import sys

from games.aigame.game import AIGame

game = AIGame(
    ["example_bot2.py", "neural_net.py"],
)
game.run()
print("ITS OVER")
game = AIGame(
    ["example_bot2.py", "neural_net.py"],
)
game.run()