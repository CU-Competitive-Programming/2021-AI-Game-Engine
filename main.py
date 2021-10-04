import sys

from games.aigame.game import AIGame

game = AIGame(
    ["example_bot2.py"] * 2,
)
game.run()
print("ITS OVER")
