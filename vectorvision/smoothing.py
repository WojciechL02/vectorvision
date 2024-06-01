from vectorvision.vertex_adjustment import _Curve
from vectorvision.utils import interval
import math
import numpy as np


# /* segment tags */
POTRACE_CURVETO = 1
POTRACE_CORNER = 2


def calculate_alpha(
    point0: tuple[float, float],
    point1: tuple[float, float],
    point2: tuple[float, float],
) -> float:
    """Calculate the parameter alpha of Bezier curve necessary for corner detection and smoothing

    Args:
        point0: starting point
        point1: vertex point
        point2: end point

    Returns:
        value of alpha parameter
    """

    point0_np = np.array(point0)
    point1_np = np.array(point1)
    point2_np = np.array(point2)

    l1_norm_p0_p2 = np.linalg.norm(point2_np - point0_np, ord=1)
    if l1_norm_p0_p2 != 0.0:
        cross_product_p1_p0_p2_p0 = np.cross(
            point1_np - point0_np, point2_np - point0_np
        )
        factor_of_proportionality = math.fabs(cross_product_p1_p0_p2_p0 / l1_norm_p0_p2)
        if factor_of_proportionality > 1:
            gamma = 1 - 1.0 / factor_of_proportionality

        else:
            gamma = 0
        alpha = gamma / 0.75
    else:
        alpha = 4 / 3.0
    return alpha


def smooth(curve: _Curve, alphamax: float) -> None:
    """
    Calculate the point which is splitting section into two parts in given proportion

    Args:
        proportion: in which proportion segment should be splitted, ratio ax/ab
        a: first point
        b: second point

    Returns:
        point splitting segment ab in given proportion
    """

    n_of_segments = curve.n

    for i in range(n_of_segments):
        j = (i + 1) % n_of_segments
        k = (i + 2) % n_of_segments

        alpha = calculate_alpha(curve[i].vertex, curve[j].vertex, curve[k].vertex)
        p4 = interval(1 / 2.0, curve[j].vertex, curve[k].vertex)

        if alpha >= alphamax:  # corner found

            curve[j].tag = POTRACE_CORNER
            curve[j].c[1] = curve[j].vertex
            curve[j].c[2] = p4

        else:
            if alpha < 0.55:
                alpha = 0.55
            elif alpha > 1:
                alpha = 1
            p2 = interval(0.5 + 0.5 * alpha, curve[i].vertex, curve[j].vertex)
            p3 = interval(0.5 + 0.5 * alpha, curve[k].vertex, curve[j].vertex)
            curve[j].tag = POTRACE_CURVETO
            curve[j].c[0] = p2
            curve[j].c[1] = p3
            curve[j].c[2] = p4

    return curve
