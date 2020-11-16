from enum import IntEnum


class Units(IntEnum):
    gatherer = 0
    weak_melee = 1
    strong_melee = 2
    weak_ranged = 3
    strong_ranged = 4


class Terrain(IntEnum):
    open: 0
    mountain: 1
    water: 2
    wood: 3
    metal: 4
