import os
import json
from typing import Union

import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def json_dumps(*args, **kwargs):
    return json.dumps(*args, **kwargs, cls=NpEncoder)


def raycast(start: Union[tuple[int, 2], np.ndarray], end: tuple[int, 2]) -> set[tuple]:
    """
    https://gamedev.stackexchange.com/questions/20103/finding-which-tiles-are-intersected-by-a-line-without-looping-through-all-of-th

    :param start: Start position
    :param end: End position
    :return: List of intersecting tiles
    """
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x = x0
    y = y0
    ns = 1 + dx + dy
    x_inc = 1 if (x1 > x0) else -1
    y_inc = 1 if (y1 > y0) else -1
    dx *= 2
    dy *= 2
    error = dx - dy

    tiles = set()

    for n in range(int(ns), 0, -1):
        tiles.add((x, y))
        if error > 0:
            x += x_inc
            error -= dy
        elif error < 0:
            y += y_inc
            error += dx
        elif error == 0:
            x += x_inc
            y += y_inc
            error -= dy
            error += dx

    return tiles
