from src.decompose import bm_to_paths_list
from src.polygons import get_best_polygon, calc_longest_straight_subpaths
from src.vertex_adjustment import adjust_vertices
from src.smoothing import smooth, POTRACE_CORNER, POTRACE_CURVETO
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
import matplotlib.patches as patches

def write(fp, curves):
    fp.write(f'''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{image.width}" height="{image.height}" viewBox="0 0 {image.width} {image.height}">''')
    parts = list()
    for curve in curves:
        first_segment = curve.segments[-1].c[2]
        parts.append(f"M{first_segment[0]},{first_segment[1]}")
        for segment in curve.segments:
            if segment.tag == POTRACE_CURVETO:
                a = segment.c[0]  
                b = segment.c[1]
                c = segment.c[2]
                parts.append(f"C{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]}")
            else:
                a = segment.c[1]
                b = segment.c[2]
                parts.append(f"Q{a[0]},{a[1]} {b[0]},{b[1]}")
        parts.append("z")
    fp.write(f'<path stroke="none" fill="black" fill-rule="evenodd" d="{"".join(parts)}"/>')
    fp.write("</svg>")


if __name__ == '__main__':

    image = Image.open('test.png')
    np_image = np.array(image).astype('bool')
    plt.imshow(np_image)
    plt.show()

    paths_list = bm_to_paths_list(np.invert(np_image))
    polygons = [get_best_polygon(path) for path in paths_list]
    longest_straights = [calc_longest_straight_subpaths(path) for path in paths_list]
    curves = list()

    fig, ax = plt.subplots()
    for path in paths_list:
        verts = np.vstack([np.array(path), path[0]])
        codes = [
            PlotPath.MOVETO,
        ]   
        codes += [PlotPath.LINETO for _ in range(verts.shape[0]-2)]
        codes.append(PlotPath.CLOSEPOLY)
        verts
        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(path_to_draw, facecolor=(0,0,0,0), edgecolor='orange', lw=5)

        ax.add_patch(patch)
    plt.imshow(image, cmap='gray')
    plt.show()


    fig, ax = plt.subplots()
    for path, polygon in zip(paths_list, longest_straights):
        index_list = np.unique(np.array(polygon))
        verts = np.vstack([np.array(path)[index_list], path[0]])
        codes = [
            PlotPath.MOVETO,
        ]   
        codes += [PlotPath.LINETO for _ in range(verts.shape[0]-2)]
        codes.append(PlotPath.CLOSEPOLY)
        verts
        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(path_to_draw, facecolor=(0,0,0,0), edgecolor='orange', lw=5)

        ax.add_patch(patch)
    plt.imshow(image, cmap='gray')
    plt.show()

    fig, ax = plt.subplots()
    for path, (polygon, m) in zip(paths_list, polygons):
        curve = adjust_vertices(path, polygon, m)
        smooth_curve = smooth(curve, 0.5)
        curves.append(smooth_curve)
        verts = [(smooth_curve.segments[0].c[0])]
        codes = [
            PlotPath.MOVETO
        ]
        for segment in smooth_curve.segments:
            if segment.tag == POTRACE_CURVETO:
                verts += [segment.c[0], segment.c[1], segment.c[2]]
                codes += [PlotPath.CURVE4, PlotPath.CURVE4, PlotPath.CURVE4]
            else:
                verts += [segment.c[1], segment.c[2]]
                codes += [PlotPath.CURVE3, PlotPath.CURVE3]
        

        path_to_draw = PlotPath(verts, codes)
        patch = patches.PathPatch(path_to_draw, facecolor=(0,0,0,0), edgecolor='orange', lw=5)
        ax.add_patch(patch)

    plt.imshow(np_image, cmap='gray')
    plt.show()



    with open('test.svg', '+w') as fh:
        write(fh, curves)
