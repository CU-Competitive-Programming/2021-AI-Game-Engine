import random

import noise
import numpy as np

# from scipy.misc import toimage

debug = False

chunksize = 1

# shape = (64, 64)
# scale = 100.0
# octaves = 2
# persistence = .8
# lacunarity = 5

shape = 1024, 1024
scale = 100.0
octaves = 12
persistence = 0.5
lacunarity = 2.0

d = random.randint(0, 100)
world = np.zeros(shape)
for i in range(shape[0]):
    for j in range(shape[1]):
        world[i][j] = noise.pnoise2(i / scale,
                                    j / scale,
                                    octaves=octaves,
                                    persistence=persistence,
                                    lacunarity=lacunarity,
                                    repeatx=shape[0],
                                    repeaty=shape[1],
                                    base=d)


# world *= scale
# world += 50


def mirror(seq):
    output = list(seq[::-1])
    output.extend(seq[1:])
    return output


world = np.array(mirror([mirror(sublist) for sublist in world]))

chunks = np.zeros((shape[0] // chunksize, shape[1] // chunksize))
for x in range(shape[0] // chunksize):
    for y in range(shape[1] // chunksize):
        chunk = world[x * chunksize: x * chunksize + chunksize, y * chunksize: y * chunksize + chunksize]

        chunks[x][y] = chunk.mean()

print(chunks)
import pandas as pd
import matplotlib.pyplot as plot

plot.hist(world.flatten())
plot.show()

print(world.max(), world.min())


def norm(x):
    if x < -0.05:
        return 1
    # elif x < 0:
    #     return 1
    elif x < 1.0:
        return 0

    # if -.2 < x < 0.2:
    #     return 0
    # if -.2 <= x <= -.3:
    #     return 2
    # if .2 >= x >= .3:
    #     return 3
    #
    # return 1


vf = np.vectorize(norm)
adjworld = vf(world)
adjchunk = vf(chunks)
print(adjchunk)


import pygame
import pygame.locals


def load_tile_table(filename, width, height):
    image = pygame.image.load(filename).convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(0, image_width // width):
        line = []
        tile_table.append(line)
        for tile_y in range(0, image_height // height):
            rect = (tile_x * width, tile_y * height, width, height)
            line.append(image.subsurface(rect))
    return tile_table


pygame.init()
# screen = pygame.display.set_mode((adjchunk.shape[0] * 16, adjchunk.shape[1] * 16))
screen = pygame.display.set_mode((adjchunk.shape[0], adjchunk.shape[1]))
screen.fill((255, 255, 255))
# table = np.array(load_tile_table("assets/sheet.png", 16, 16))
table = np.array(load_tile_table("assets/sheet.png", 1, 1))

grass = table[0:3, 0]
rock = table[0 * 16: 1 * 16, 24 * 16 + 4] #table[5 * 16: 6 * 16, 16 + 4]  # water
metal = table[6:8, 7 * 16 + 3]
wood = table[2 * 16 + 4:2 * 16 + 8, 16 + 4]
# grass = table[0:3, 0]
# rock = table[3:6, 1]
# metal = table[6:7, 29]
# wood = table[4:7, 0]

for x, row in enumerate(adjchunk):
    for y, tile in enumerate(row):
        # pos = (x * 16, y * 16)
        pos = x, y
        if tile == 0:
            screen.blit(random.choice(grass), pos)
        elif tile == 1:
            screen.blit(random.choice(grass), pos)
            screen.blit(random.choice(rock), pos)
        elif tile == 2:
            screen.blit(random.choice(grass), pos)
            screen.blit(random.choice(metal), pos)
        elif tile == 3:
            screen.blit(random.choice(grass), pos)
            screen.blit(random.choice(wood), pos)

pygame.display.flip()
while pygame.event.wait().type != pygame.locals.QUIT:
    pass
