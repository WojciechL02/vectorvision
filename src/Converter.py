from PIL import ImageOps, Image
import time
import os
import numpy as np
from src.path_decomposition import Bitmap
from src.smoothing import smooth, POTRACE_CURVETO
from src.polygons import get_best_polygon
from src.vertex_adjustment import adjust_vertices, _Curve
from contextlib import contextmanager
from typing import TextIO


@contextmanager
def create_svg(name: str, width: int, height: int):
    file = open(f"{name}.svg", "+w")
    file.write(
        f"""<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
                  width="{width}" height="{height}" viewBox="0 0 {width} {height}">"""
    )
    try:
        yield file
    finally:
        file.write("</svg>")
        file.close()


class Converter:
    def __init__(self, image: Image):
        self.image = image
        self.num_colors = len(image.getcolors(17000000))

    def run(self, path):
        s = time.process_time()
        with create_svg(path, self.image.width, self.image.height) as fh:
            if self.num_colors == 2:
                print("BINARY")
                a = np.array(self.image)
                color_table = np.where(
                    np.isin(a, np.arange(1)),
                    0,
                    1,
                )
                self.convert_single_color(color_table, fh)
            else:
                print("GRAYSCALE")
                self.image = ImageOps.grayscale(self.image)
                a = np.array(self.image)
                for color in range(0, 256, 32):
                    color_table = np.where(
                        np.isin(a, np.arange(color, color + 32)),
                        0,
                        1,
                    )
                    self.convert_single_color(color_table, fh, color=color)
        e = time.process_time()
        print(f"Finished in {round(e - s, 2)} s\n")

    def convert_single_color(self, color_table, fh, color=0):
        try:
            if not np.all(color_table):
                bm = Bitmap(color_table)
                paths_list = bm.generate_paths_list()
                polygons = [get_best_polygon(path) for path in paths_list]

                curves = list()

                for path, polygon in zip(paths_list, polygons):
                    curve = adjust_vertices(path, polygon)
                    smooth_curve = smooth(curve, 0.5)
                    curves.append(smooth_curve)
                self._write_path_to_svg(fh, curves, color)
        except Exception:
            pass

    def _write_path_to_svg(self, fp: TextIO, curves: list[_Curve], color: int) -> None:
        """Writes path of given color to the SVG file."""

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

        rgb_color = (color, color, color)

        fp.write(
            f'<path stroke="none" fill="rgb{rgb_color}" fill-rule="evenodd" d="{"".join(parts)}"/>'
        )
