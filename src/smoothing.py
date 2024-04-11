from vectorvision.src.vertex_adjustment import _Curve
from vectorvision.src.polygons import mod, sign
import math

# /* segment tags */
POTRACE_CURVETO = 1
POTRACE_CORNER = 2

def dorth_infty(p0, p2):
    """
    return a direction that is 90 degrees counterclockwise from p2-p0,
    but then restricted to one of the major wind directions (n, nw, w, etc)
    """
    return (-sign(p2[1] - p0[1]), sign(p2[0] - p0[0]))


def dpara(p0, p1, p2) -> float:
    """
    /* return (p1-p0)x(p2-p0), the area of the parallelogram */
    """
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p2[0] - p0[0]
    y2 = p2[1] - p0[1]
    return x1 * y2 - x2 * y1


def ddenom(p0, p2) -> float:
    """
    ddenom/dpara have the property that the square of radius 1 centered
    at p1 intersects the line p0p2 iff |dpara(p0,p1,p2)| <= ddenom(p0,p2)
    """
    r = dorth_infty(p0, p2)
    return r[1] * (p2[0] - p0[0]) - r[0] * (p2[1] - p0[1])


def interval(t: float, a, b):
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def reverse(curve: _Curve) -> None:
    """/* reverse orientation of a path */"""
    m = curve.n
    i = 0
    j = m - 1
    while i < j:
        tmp = curve[i].vertex
        curve[i].vertex = curve[j].vertex
        curve[j].vertex = tmp
        i += 1
        j -= 1


# /* Always succeeds */


def smooth(curve: _Curve, alphamax: float) -> None:
    m = curve.n

    # /* examine each vertex and find its best fit */
    for i in range(m):
        j = mod(i + 1, m)
        k = mod(i + 2, m)
        p4 = interval(1 / 2.0, curve[k].vertex, curve[j].vertex)

        denom = ddenom(curve[i].vertex, curve[k].vertex)
        if denom != 0.0:
            dd = dpara(curve[i].vertex, curve[j].vertex, curve[k].vertex) / denom
            dd = math.fabs(dd)
            alpha = (1 - 1.0 / dd) if dd > 1 else 0
            alpha = alpha / 0.75
        else:
            alpha = 4 / 3.0
        curve[j].alpha0 = alpha  # /* remember "original" value of alpha */

        if alpha >= alphamax:  # /* pointed corner */
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
        curve[j].alpha = alpha  # /* store the "cropped" value of alpha */
        curve[j].beta = 0.5

    curve.alphacurve = True

    return curve