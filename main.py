from PIL import Image
import argparse
import numpy as np
from vectorvision.smoothing import smooth, POTRACE_CURVETO
from vectorvision.decompose import bm_to_paths_list
from vectorvision.polygons import get_best_polygon
from vectorvision.vertex_adjustment import adjust_vertices, _Curve
from typing import TextIO


def write_to_svg(fp: TextIO, curves: list[_Curve], width: int, height: int) -> None:

    """Write image described as list of curves in the svg format"""

    fp.write(
        f"""<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
          width="{width}" height="{height}" viewBox="0 0 {width} {height}">"""
    )
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
    fp.write(
        f'<path stroke="none" fill="black" fill-rule="evenodd" d="{"".join(parts)}"/>'
    )
    fp.write("</svg>")


def convert(image: Image) -> list[_Curve]:

    """ Take image as an input and go through all stages of conversion with it.
        Returns list of curves creating the resulting vector image"""

    np_image = np.array(image).astype("bool")
    paths_list = bm_to_paths_list(np.invert(np_image))
    polygons = [get_best_polygon(path) for path in paths_list]

    curves = list()

    for path, polygon in zip(paths_list, polygons):
        curve = adjust_vertices(path, polygon)
        smooth_curve = smooth(curve, 0.5)
        curves.append(smooth_curve)

    return curves


def main() -> None:
    parser = argparse.ArgumentParser(
        description="vectorvision - CLI tool for raster graphics vectorizing"
    )

    parser.add_argument("-i", "--input-path", type=str, required=True)
    parser.add_argument("-o", "--output-path", type=str, required=True)

    args = parser.parse_args()

    image = Image.open(args.input_path)
    curves = convert(image)

    with open(args.output_path, "+w") as fh:
        write_to_svg(fh, curves, image.width, image.height)


if __name__ == "__main__":
    main()
