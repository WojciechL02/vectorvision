from vectorvision.decompose import bm_to_paths_list

from vectorvision.polygons import get_best_polygon, get_longest_straight_subpaths
from vectorvision.vertex_adjustment import adjust_vertices
from vectorvision.smoothing import smooth, POTRACE_CORNER, POTRACE_CURVETO
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
import matplotlib.patches as patches


if __name__ == "__main__":
    # ----- load and draw image -----
    image = Image.open("test.png")
    np_image = np.array(image).astype("bool")
    plt.imshow(np_image)
    plt.show()

    # ===== GENERATE PATHS LIST =====
    paths_list = bm_to_paths_list(np.invert(np_image))
    polygons = [get_best_polygon(path) for path in paths_list]
    longest_straights = [get_longest_straight_subpaths(path) for path in paths_list]
    curves = list()

    fig, ax = plt.subplots()
    for path in paths_list:
        verts = np.vstack([np.array(path), path[0]])
        codes = [
            PlotPath.MOVETO,
        ]
        codes += [PlotPath.LINETO for _ in range(verts.shape[0] - 2)]
        codes.append(PlotPath.CLOSEPOLY)
        verts
        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(
            path_to_draw, facecolor=(0, 0, 0, 0), edgecolor="orange", lw=2
        )

        ax.add_patch(patch)
    plt.imshow(image, cmap="gray")
    plt.show()

    fig, ax = plt.subplots()
    for path, polygon in zip(paths_list, longest_straights):
        index_list = np.unique(np.array(polygon))
        verts = np.vstack([np.array(path)[index_list], path[0]])
        codes = [
            PlotPath.MOVETO,
        ]
        codes += [PlotPath.LINETO for _ in range(verts.shape[0] - 2)]
        codes.append(PlotPath.CLOSEPOLY)
        verts
        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(
            path_to_draw, facecolor=(0, 0, 0, 0), edgecolor="orange", lw=2
        )

        ax.add_patch(patch)
    plt.imshow(image, cmap="gray")
    plt.show()

    fig, ax = plt.subplots()
    for path, (polygon, m) in zip(paths_list, polygons):
        curve = adjust_vertices(path, polygon, m)
        smooth_curve = smooth(curve, 0.5)
        curves.append(smooth_curve)
        verts = [(smooth_curve.segments[0].c[0])]
        codes = [PlotPath.MOVETO]
        for segment in smooth_curve.segments:
            if segment.tag == POTRACE_CURVETO:
                verts += [segment.c[0], segment.c[1], segment.c[2]]
                codes += [PlotPath.CURVE4, PlotPath.CURVE4, PlotPath.CURVE4]
            else:
                verts += [segment.c[1], segment.c[2]]
                codes += [PlotPath.CURVE3, PlotPath.CURVE3]

        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(
            path_to_draw, facecolor=(0, 0, 0, 0), edgecolor="orange", lw=2
        )
        ax.add_patch(patch)

    plt.imshow(np_image, cmap="gray")
    plt.show()

    with open("test.svg", "+w") as fh:
        write(fh, curves)
