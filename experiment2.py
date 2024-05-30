from src.path_decomposition import Bitmap
from src.polygons import get_best_polygon, calc_longest_straight_subpaths
from src.vertex_adjustment import adjust_vertices
from src.smoothing import smooth, POTRACE_CORNER, POTRACE_CURVETO
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
import matplotlib.patches as patches





if __name__ == "__main__":
    # ----- load and draw image -----
    image = Image.open("images/head.pbm")
    np_image = np.array(image).astype("bool")
    plt.imshow(np_image)
    plt.show()

    # ===== GENERATE PATHS LIST =====
    bm = Bitmap(np_image)
    paths_list = bm.generate_paths_list()
    polygons = [get_best_polygon(path) for path in paths_list]
    longest_straights = [calc_longest_straight_subpaths(path) for path in paths_list]
    print(paths_list)
    print(longest_straights)
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


    for path, polygon in zip(paths_list, polygons):
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
            path_to_draw, facecolor=(0, 0, 0, 0), edgecolor="green", lw=2
        )

        ax.add_patch(patch)
    plt.imshow(image, cmap="gray")
    plt.show()

    fig, ax = plt.subplots()
    for path, polygon in zip(paths_list, polygons):
        curve = adjust_vertices(path, polygon)
        curves.append(curve)
        verts = np.vstack([np.array([x.vertex for x in curve.segments]), curve.segments[0].vertex])
        codes = [
            PlotPath.MOVETO,
        ]
        codes += [PlotPath.LINETO for _ in range(verts.shape[0] - 2)]
        codes.append(PlotPath.CLOSEPOLY)
        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(
            path_to_draw, facecolor=(0, 0, 0, 0), edgecolor="orange", lw=2
        )

        ax.add_patch(patch)
        ax.add_patch(patch)

    plt.imshow(np_image, cmap="gray")
    plt.show()

    fig, ax = plt.subplots()
    for path, polygon in zip(paths_list, polygons):
        curve = adjust_vertices(path, polygon)
        smooth_curve = smooth(curve, 1.5)
        curves.append(smooth_curve)
        verts = [(smooth_curve.segments[0].c[0])]
        codes = [PlotPath.MOVETO]
        for segment in smooth_curve.segments:
            if segment.tag == POTRACE_CURVETO:
                verts += [segment.c[0], segment.c[1], segment.c[2]]
                codes += [PlotPath.CURVE4, PlotPath.CURVE4, PlotPath.CURVE4]
            else:
                verts += [segment.c[1], segment.c[2]]
                codes += [PlotPath.LINETO, PlotPath.LINETO]

        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(
            path_to_draw, facecolor=(0, 0, 0, 0), edgecolor="orange", lw=2
        )
        ax.add_patch(patch)

    plt.imshow(np_image, cmap="gray")
    plt.show()