from src.vertex_adjustment import _Curve
from src.utils import interval
import numpy as np
import math

POTRACE_CURVETO = 1
POTRACE_CORNER = 2
COS179 = math.cos(math.radians(179))


def calculate_distance(p: tuple[float, float], q: tuple[float, float]) -> float:
    """Calculates Euclidean distance between two points in 2D space.

    Args:
            p: first point
            q: second point

    Returns:
        Value of the Euclidean distance (float).
    """
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def dpara(p0, p1, p2) -> float:
    """Calculates the area of the parallelogram in the 2D space.
    The parallelogram is defined by three points.
    This function is also used to determine curve convexity.

    Args:
        p0: first point
        p1: second point
        p2: third point

    Returns:
        Area = (p1 - p0) x (p2 - p0) Can be also negative.
    """
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p2[0] - p0[0]
    y2 = p2[1] - p0[1]
    return np.cross([x1, y1], [x2, y2]).item()


def cprod(p0, p1, p2, p3) -> float:
    """Calculates a cross product of differences between points: (p1-p0)x(p3-p2).

    Args:
        p0, p1, p2, p3: points
    Returns:
        Value of cross product (float).
    """
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p3[0] - p2[0]
    y2 = p3[1] - p2[1]
    return x1 * y2 - x2 * y1


def iprod(p0, p1, p2, p3=None) -> float:
    """Calculates the product: (p1-p0) * (p3-p2) if there are four points given or
    (p1-p0) * (p2-p0) otherwise.

    Args:
        p0, p1, p2, p3=None: points

    Returns:
        Value of the product (float).
    """
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p3[0] - p2[0] if p3 else p2[0] - p0[0]
    y2 = p3[1] - p2[1] if p3 else p2[1] - p0[1]
    return x1 * x2 + y1 * y2


def bezier(t: float, p0, p1, p2, p3):
    """Calculates a point of a bezier curve specified by control points and t param.

    Paper:
    "We restrict ourselves to the case where the straight lines through p0p1
    and through p3p2 intersect at a point o (i.e., they are not parallel)."

    Args:
        p0, p1, p2, p3: Bezier curve control points
        t: Curve parameter

    Returns:
        Point
    """
    s = 1 - t
    x = (
        pow(s, 3) * p0[0]
        + 3 * pow(s, 2) * t * p1[0]
        + 3 * pow(t, 2) * s * p2[0]
        + pow(t, 3) * p3[0]
    )
    y = (
        pow(s, 3) * p0[1]
        + 3 * pow(s, 2) * t * p1[1]
        + 3 * pow(t, 2) * s * p2[1]
        + pow(t, 3) * p3[1]
    )
    return x, y


def tangent(p0, p1, p2, p3, q0, q1) -> float:
    """Calculates the point t in [0..1] on the (convex) bezier curve
    (p0,p1,p2,p3) which is tangent to q1-q0. Return -1 if there is no
    solution in [0..1].

    Args:
        p0, p1, p2, p3: control points of Bezier curve
        q0, q1:
    Returns:
          Value of t if there is solution in [0..1], otherwise -1.
    """

    A = cprod(p0, p1, q0, q1)
    B = cprod(p1, p2, q0, q1)
    C = cprod(p2, p3, q0, q1)

    a = A - 2 * B + C
    b = -2 * A + 2 * B
    c = A
    delta = b * b - 4 * a * c

    if a == 0 or delta < 0:
        return -1

    root1, root2 = np.roots([a, b, c])
    if 0 <= root1 <= 1:
        return root1
    elif 0 <= root2 <= 1:
        return root2
    return -1


class opti_t:
    def __init__(self):
        self.pen = 0  # /* penalty */
        self.c = [(0, 0), (0, 0)]  # /* curve parameters */
        self.t = 0  # /* curve parameters */
        self.s = 0  # /* curve parameters */
        self.alpha = 0  # /* curve parameter */


def calculate_optimization_penalty(
    curve: _Curve,
    i: int,
    j: int,
    res: opti_t,
    opttolerance: float,
    convc: int,
    areac: float,
) -> int:
    """
    /* calculate best fit from i+.5 to j+.5.    Assume i<j (cyclically).
     Return 0 and set badness and parameters (alpha, beta), if
     possible. Return 1 if impossible. */
    """

    n_of_segments = curve.n

    # /* check convexity, corner-freeness, and maximum bend < 179 degrees */

    if i == j:  # sanity - a full loop can never be an opticurve
        return 1

    k = i
    i1 = (i + 1) % n_of_segments
    k1 = (k + 1) % n_of_segments

    conv = convc[k1]
    if conv == 0:
        return 1
    d = calculate_distance(curve[i].vertex, curve[i1].vertex)
    k = k1
    while k != j:
        k1 = (k + 1) % n_of_segments
        k2 = (k + 2) % n_of_segments
        if convc[k1] != conv:
            return 1
        if (
            np.sign(
                cprod(
                    curve[i].vertex,
                    curve[i1].vertex,
                    curve[k1].vertex,
                    curve[k2].vertex,
                )
            )
            != conv
        ):
            return 1
        if (
            iprod(
                curve[i].vertex,
                curve[i1].vertex,
                curve[k1].vertex,
                curve[k2].vertex,
            )
            < d * calculate_distance(curve[k1].vertex, curve[k2].vertex) * COS179
        ):
            return 1
        k = k1

    # /* the curve we're working in: */
    p0 = curve[i % n_of_segments].c[2]
    p1 = curve[(i + 1) % n_of_segments].vertex
    p2 = curve[j % n_of_segments].vertex
    p3 = curve[j % n_of_segments].c[2]

    # /* determine its area */
    area = areac[j] - areac[i]
    area -= dpara(curve[0].vertex, curve[i].c[2], curve[j].c[2]) / 2
    if i >= j:
        area += areac[n_of_segments]

    # /* find intersection o of p0p1 and p2p3. Let t,s such that
    # o =interval(t,p0,p1) = interval(s,p3,p2). Let A be the area of the
    # triangle (p0,o,p3). */

    A1 = dpara(p0, p1, p2)
    A2 = dpara(p0, p1, p3)
    A3 = dpara(p0, p2, p3)
    # /* A4 = dpara(p1, p2, p3); */
    A4 = A1 + A3 - A2

    if A2 == A1:  # this should never happen
        return 1

    t = A3 / (A3 - A4)
    s = A2 / (A2 - A1)
    A = A2 * t / 2.0

    if A == 0.0:  # this should never happen
        return 1

    R = area / A  # /* relative area */
    alpha = 2 - math.sqrt(4 - R / 0.3)  # /* overall alpha for p0-o-p3 curve */

    res.c[0] = interval(t * alpha, p0, p1)
    res.c[1] = interval(s * alpha, p3, p2)
    res.alpha = alpha
    res.t = t
    res.s = s

    p1 = res.c[0]
    # p1 = _Point(p1.x, p1.y)
    p2 = res.c[1]  # /* the proposed curve is now (p0,p1,p2,p3) */
    # p2 = _Point(p2.x, p2.y)

    res.pen = 0

    # /* calculate penalty */
    # /* check tangency with edges */
    k = (i + 1) % n_of_segments
    while k != j:
        k1 = (k + 1) % n_of_segments
        t = tangent(p0, p1, p2, p3, curve[k].vertex, curve[k1].vertex)
        if t < -0.5:
            return 1
        pt = bezier(t, p0, p1, p2, p3)
        d = calculate_distance(curve[k].vertex, curve[k1].vertex)
        if d == 0.0:  # /* this should never happen */
            return 1
        d1 = dpara(curve[k].vertex, curve[k1].vertex, pt) / d
        if math.fabs(d1) > opttolerance:
            return 1
        if (
            iprod(curve[k].vertex, curve[k1].vertex, pt) < 0
            or iprod(curve[k1].vertex, curve[k].vertex, pt) < 0
        ):
            return 1
        res.pen += d1**2
        k = k1

    # /* check corners */
    k = i
    while k != j:
        k1 = (k + 1) % n_of_segments
        t = tangent(p0, p1, p2, p3, curve[k].c[2], curve[k1].c[2])
        if t < -0.5:
            return 1
        pt = bezier(t, p0, p1, p2, p3)
        d = calculate_distance(curve[k].c[2], curve[k1].c[2])
        if d == 0.0:  # /* this should never happen */
            return 1
        d1 = dpara(curve[k].c[2], curve[k1].c[2], pt) / d
        d2 = dpara(curve[k].c[2], curve[k1].c[2], curve[k1].vertex) / d
        d2 *= 0.75 * curve[k1].alpha
        if d2 < 0:
            d1 = -d1
            d2 = -d2
        if d1 < d2 - opttolerance:
            return 1
        if d1 < d2:
            res.pen += (d1 - d2) ** 2
        k = k1
    return 0


def precalculate_convexity(n_of_segments, curve):
    convexity = list()

    # pre-calculate convexity: +1 = right turn, -1 = left turn, 0 = corner
    for i in range(n_of_segments):
        if curve[i].tag == POTRACE_CURVETO:
            convexity.append(
                np.sign(
                    dpara(
                        curve[(i - 1) % n_of_segments].vertex,
                        curve[i].vertex,
                        curve[(i + 1) % n_of_segments].vertex,
                    )
                )
            )
        else:
            convexity.append(0)

    return convexity


def precalculate_areas(n_of_segments, curve):
    area = 0.0
    areac = [0.0]
    p0 = curve[0].vertex
    for i in range(n_of_segments):
        i1 = (i + 1) % n_of_segments
        if curve[i1].tag == POTRACE_CURVETO:
            alpha = curve[i1].alpha
            area += (
                0.3
                * alpha
                * (4 - alpha)
                * dpara(curve[i].c[2], curve[i1].vertex, curve[i1].c[2])
                / 2
            )
            area += dpara(p0, curve[i].c[2], curve[i1].c[2]) / 2
        areac.append(area)

    return areac


def optimize_curve(curve: _Curve, opttolerance: float) -> int:
    """
    optimize the path p, replacing sequences of Bezier segments by a
    single segment when possible. Return 0 on success, 1 with errno set
    on failure.
    """
    n_of_segments = curve.n
    pt = [0] * (n_of_segments + 1)  # /* pt[m+1] */
    pen = [0.0] * (n_of_segments + 1)  # /* pen[m+1] */
    length = [0] * (n_of_segments + 1)  # /* len[m+1] */
    opt = [None] * (n_of_segments + 1)  # /* opt[m+1] */

    convc = precalculate_convexity(n_of_segments, curve)
    areac = precalculate_areas(n_of_segments, curve)

    pt[0] = -1
    pen[0] = 0
    length[0] = 0

    # /* Fixme: we always start from a fixed point
    # -- should find the best curve cyclically */

    o = None
    for j in range(1, n_of_segments + 1):
        # /* calculate best path from 0 to j */
        pt[j] = j - 1
        pen[j] = pen[j - 1]
        length[j] = length[j - 1] + 1
        for i in range(j - 2, -1, -1):
            if o is None:
                o = opti_t()
            if calculate_optimization_penalty(
                curve, i, j % n_of_segments, o, opttolerance, convc, areac
            ):
                break
            if length[j] > length[i] + 1 or (
                length[j] == length[i] + 1 and pen[j] > pen[i] + o.pen
            ):
                opt[j] = o
                pt[j] = i
                pen[j] = pen[i] + o.pen
                length[j] = length[i] + 1
                o = None
    om = length[n_of_segments]
    new_curve = _Curve(om)
    s = [None] * om
    t = [None] * om

    j = n_of_segments
    for i in range(om - 1, -1, -1):
        if pt[j] == j - 1:
            new_curve[i].tag = curve[j % n_of_segments].tag
            new_curve[i].c[0] = curve[j % n_of_segments].c[0]
            new_curve[i].c[1] = curve[j % n_of_segments].c[1]
            new_curve[i].c[2] = curve[j % n_of_segments].c[2]
            new_curve[i].vertex = curve[j % n_of_segments].vertex
            new_curve[i].alpha = curve[j % n_of_segments].alpha
            new_curve[i].alpha0 = curve[j % n_of_segments].alpha0
            new_curve[i].beta = curve[j % n_of_segments].beta
            s[i] = t[i] = 1.0
        else:
            new_curve[i].tag = POTRACE_CURVETO
            new_curve[i].c[0] = opt[j].c[0]
            new_curve[i].c[1] = opt[j].c[1]
            new_curve[i].c[2] = curve[j % n_of_segments].c[2]
            new_curve[i].vertex = interval(
                opt[j].s, curve[j % n_of_segments].c[2], curve[j % n_of_segments].vertex
            )
            new_curve[i].alpha = opt[j].alpha
            new_curve[i].alpha0 = opt[j].alpha
            s[i] = opt[j].s
            t[i] = opt[j].t
        j = pt[j]

    # /* calculate beta parameters */
    # for i in range(om):
    #     i1 = (i + 1) % om
    #     new_curve[i].beta = s[i] / (s[i] + t[i1])
    # new_curve.alphacurve = True
    return new_curve
