import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib import patches as patches


def draw_path(bitmap: np.array, path):
    verts = path
    line_to_path = len(path) - 1

    codes = [
        PlotPath.MOVETO,
    ]
    codes += [PlotPath.LINETO for _ in range(line_to_path)]

    path_to_draw = PlotPath(verts, codes)
    patch = patches.PathPatch(path_to_draw, facecolor="orange", lw=2)
    fig, ax = plt.subplots()
    ax.add_patch(patch)
    plt.imshow(bitmap)
    plt.show()
