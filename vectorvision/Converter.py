from PIL import ImageOps, Image
import time
import numpy as np
from vectorvision.path_decomposition import Bitmap
from vectorvision.smoothing import smooth, POTRACE_CURVETO
from vectorvision.polygons import get_best_polygon
from vectorvision.vertex_adjustment import adjust_vertices, _Curve
from vectorvision.curve_optimization import optimize_curve
from contextlib import contextmanager
from typing import TextIO


@contextmanager
def create_svg(name: str, width: int, height: int):
    file = open(f"{name}", "+w")
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
    def __init__(self, image: Image, turnpolicy, turdsize, alpha_max, is_long_curve, opttolreance, scale):
        self.image = image
        self.num_colors = len(image.getcolors(17000000))
        self.turnpolicy = turnpolicy
        self.turdsize = turdsize
        self.alpha_max = alpha_max
        self.is_long_curve = is_long_curve
        self.opttolerance = opttolreance
        self.scale = scale

    def run(self, path):
        s = time.process_time()
        with create_svg(path, self.image.width * self.scale, self.image.height * self.scale) as fh:
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
                step = 32
                for color in range(0, 256, step):
                    color_table = np.where(
                        np.isin(a, np.arange(0, color)),
                        0,
                        1,
                    )
                    self.convert_single_color(
                        color_table,
                        fh,
                        opacity=(1 - color / 255) * min(1, step / 60),
                    )
        e = time.process_time()
        print(f"Finished in {round(e - s, 2)} s\n")

    def convert_single_color(self, color_table, fh, opacity=1):
        if not np.all(color_table):
            bm = Bitmap(color_table)
            paths_list = bm.generate_paths_list(self.turdsize, self.turnpolicy)
            polygons = [get_best_polygon(path) for path in paths_list]
            curves = list()
            for path, polygon in zip(paths_list, polygons):
                curve = adjust_vertices(path, polygon)
                smooth_curve = smooth(curve, self.alpha_max)
                if not self.is_long_curve:
                    optimal_curve = optimize_curve(smooth_curve, self.opttolerance)
                    curves.append(optimal_curve)
                else:
                    curves.append(smooth_curve)
            self._write_path_to_svg(fh, curves, opacity)

    def _write_path_to_svg(
        self, fp: TextIO, curves: list[_Curve], opacity: float
    ) -> None:
        """Writes path of given color to the SVG file."""

        parts = list()
        for curve in curves:
            first_segment = curve.segments[-1].c[2]
            parts.append(f"M{first_segment[0] * self.scale},{first_segment[1] * self.scale}")
            for segment in curve.segments:
                if segment.tag == POTRACE_CURVETO:
                    a = segment.c[0]
                    b = segment.c[1]
                    c = segment.c[2]
                    parts.append(f"""C{a[0] * self.scale} {a[1] * self.scale},
                                  {b[0] * self.scale} {b[1] * self.scale}, {c[0] * self.scale} {c[1] * self.scale}""")
                else:
                    a = segment.c[1]
                    b = segment.c[2]
                    parts.append(f"L{a[0] * self.scale} {a[1] * self.scale} {b[0] * self.scale},{b[1] * self.scale}")
            parts.append("z")

        fp.write(
            f'<path stroke="none" opacity="{opacity} " fill-rule="evenodd" d="{"".join(parts)}"/>'
        )
