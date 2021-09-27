import sys

from games.aigame.game import AIGame

game = AIGame(
    ["example_bot.py", "example_bot2.py"],
)
game.run()
print("ITS OVER")
