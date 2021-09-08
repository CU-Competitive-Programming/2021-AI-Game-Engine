import noise
import numpy as np


def norm(x):
    if x < -0.15:
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


def mirror(seq):
    output = list(seq[::-1])
    output.extend(seq[1:])
    return output


def chunkify(world, chunksize):
    shape = world.shape

    chunks = np.zeros((shape[0] // chunksize, shape[1] // chunksize))
    for x in range(shape[0] // chunksize):
        for y in range(shape[1] // chunksize):
            chunk = world[x * chunksize: x * chunksize + chunksize, y * chunksize: y * chunksize + chunksize]

            chunks[x][y] = chunk.mean()

    return chunks


def generate_map(np_random):
    # shape = (64, 64)
    # scale = 100.0
    # octaves = 2
    # persistence = .8
    # lacunarity = 5

    shape = 15, 15
    scale = 100.0
    octaves = 12
    persistence = 0.5
    lacunarity = 2.0

    d = np_random.randint(0, 100)
    world = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            world[i][j] = noise.pnoise2(
                i / scale,
                j / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=shape[0],
                repeaty=shape[1],
                base=d
            )

    # world *= scale
    # world += 50

    world = np.array(mirror([mirror(sublist) for sublist in world]))
    return vf(world)
