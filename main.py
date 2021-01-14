import sys

from games.aigame.game import AIGame

game = AIGame(
    [".\\example_bot.py"] * 2
)
game.run()