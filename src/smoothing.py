from src.vertex_adjustment import _Curve
import math
import numpy as np

# /* segment tags */
POTRACE_CURVETO = 1
POTRACE_CORNER = 2


def interval(t: float, a, b):
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def calculate_alpha(point0, point1, point2):
    point0_np = np.array(point0)
    point1_np = np.array(point1)
    point2_np = np.array(point2)

    l1_norm_p0_p2 = np.linalg.norm(point2_np-point0_np, ord=1)
    if l1_norm_p0_p2 != 0.0:
        cross_product_p1_p0_p2_p0 = np.cross(point1_np-point0_np, point2_np-point0_np)
        factor_of_proportionality = math.fabs(cross_product_p1_p0_p2_p0 / l1_norm_p0_p2)
        if factor_of_proportionality > 1:
            gamma = (1 - 1.0 / factor_of_proportionality)
        else:
            gamma = 0
        alpha = gamma / 0.75
    else:
        alpha = 4 / 3.0
    return alpha


def smooth(curve: _Curve, alphamax: float) -> None:
    n_of_segments = curve.n

    # /* examine each vertex and find its best fit */
    for i in range(n_of_segments):
        j = (i + 1) % n_of_segments
        k = (i + 2) % n_of_segments

        alpha = calculate_alpha(curve[i].vertex, curve[j].vertex, curve[k].vertex)
        p4 = interval(1 / 2.0, curve[j].vertex, curve[k].vertex)

        if alpha >= alphamax:  # /* pointed corner */

            curve[j].tag = POTRACE_CORNER
            curve[j].c[1] = curve[j].vertex
            curve[j].c[2] = p4
        else:
            # if alpha < 0.55:
            #     alpha = 0.55
            # elif alpha > 1:
            #     alpha = 1
            p2 = interval(alpha, curve[i].vertex, curve[j].vertex)
            p3 = interval(alpha, curve[k].vertex, curve[j].vertex)
            curve[j].tag = POTRACE_CURVETO
            curve[j].c[0] = p2
            curve[j].c[1] = p3
            curve[j].c[2] = p4
        # curve[j].alpha = alpha  # /* store the "cropped" value of alpha */

    return curve
