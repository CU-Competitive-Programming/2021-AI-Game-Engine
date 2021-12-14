import sys

from games.aigame.game import AIGame

for i in range(6668, 6668+50):
    game = AIGame(
        ["example_bot2.py", "neural_net.py"],
        port=i
    )
    game.run()
    print("ITS OVER")
