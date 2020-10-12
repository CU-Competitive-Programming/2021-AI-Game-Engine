import numpy as np

from engine import Game

game = Game()

group = game.create_group(np.array([0, 0]))

for x in range(5):
    unit = game.create_unit(5, x + 1, 5, 5, 5, 5, 5, np.array([0, 0]))
    print(unit)
    group.add_member(unit)

print("Initial position", group.position)
print("Group speed", group.speed)
print(group)

group.move((0, 5))
print("First move", group.position, group.members[0].position)
print("Queued moves", group.queued_moves)
group.process_turn()
print(group.position, group.members[0].position)
