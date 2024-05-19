from vertex_adjustment import _Curve
import numpy as np
import math
POTRACE_CURVETO = 1
POTRACE_CORNER = 2
COS179 = math.cos(math.radians(179))


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def interval(t: float, a, b):
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def ddist(p, q) -> float:
    """calculate distance between two points"""
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def dpara(p0, p1, p2) -> float:
    """
    /* return (p1-p0)x(p2-p0), the area of the parallelogram */
    """
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p2[0] - p0[0]
    y2 = p2[1] - p0[1]
    if x1 * y2 - x2 * y1 != np.cross([p1[0]-p0[0], p1[1]-p0[1]], [p2[0]-p0[0], p2[1]-p0[1]]):
        print(x1 * y2 - x2 * y1, np.cross([p1[0]-p0[0], p1[1]-p1[1]], [p2[0]-p0[0], p2[1]-p0[1]]))
    return x1 * y2 - x2 * y1


def cprod(p0, p1, p2, p3) -> float:
    """calculate (p1-p0)x(p3-p2)"""
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p3[0] - p2[0]
    y2 = p3[1] - p2[1]
    return x1 * y2 - x2 * y1


def iprod1(p0, p1, p2, p3) -> float:
    """calculate (p1-p0)*(p3-p2)"""
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p3[0] - p2[0]
    y2 = p3[1] - p2[1]
    return x1 * x2 + y1 * y2


def bezier(t: float, p0, p1, p2, p3):
    """calculate point of a bezier curve"""
    s = 1 - t

    """
    Note: a good optimizing compiler (such as gcc-3) reduces the
    following to 16 multiplications, using common subexpression
    elimination.
    """
    return (
        s * s * s * p0[0]
        + 3 * (s * s * t) * p1[0]
        + 3 * (t * t * s) * p2[0]
        + t * t * t * p3[0],
        s * s * s * p0[1]
        + 3 * (s * s * t) * p1[1]
        + 3 * (t * t * s) * p2[1]
        + t * t * t * p3[1],
    )


def tangent(
    p0, p1, p2, p3, q0, q1
) -> float:
    """calculate the point t in [0..1] on the (convex) bezier curve
    (p0,p1,p2,p3) which is tangent to q1-q0. Return -1.0 if there is no
    solution in [0..1]."""

    # (1-t)^2 A + 2(1-t)t B + t^2 C = 0
    # a t^2 + b t + c = 0

    A = cprod(p0, p1, q0, q1)
    B = cprod(p1, p2, q0, q1)
    C = cprod(p2, p3, q0, q1)

    a = A - 2 * B + C
    b = -2 * A + 2 * B
    c = A

    d = b * b - 4 * a * c

    if a == 0 or d < 0:
        return -1.0

    s = math.sqrt(d)

    r1 = (-b + s) / (2 * a)
    r2 = (-b - s) / (2 * a)

    if 0 <= r1 <= 1:
        return r1
    elif 0 <= r2 <= 1:
        return r2
    else:
        return -1.0
    

def iprod(p0, p1, p2) -> float:
    """calculate (p1-p0)*(p2-p0)"""
    x1 = p1[0] - p0[0]
    y1 = p1[1] - p0[1]
    x2 = p2[0] - p0[0]
    y2 = p2[1] - p0[1]
    return x1 * x2 + y1 * y2


class opti_t:
    def __init__(self):
        self.pen = 0  # /* penalty */
        self.c = [(0, 0), (0, 0)]  # /* curve parameters */
        self.t = 0  # /* curve parameters */
        self.s = 0  # /* curve parameters */
        self.alpha = 0  # /* curve parameter */


def opti_penalty(
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
    d = ddist(curve[i].vertex, curve[i1].vertex)
    k = k1
    while k != j:
        k1 = k + 1 % n_of_segments
        k2 = k + 2 % n_of_segments
        if convc[k1] != conv:
            return 1
        if (
            sign(
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
            iprod1(
                curve[i].vertex,
                curve[i1].vertex,
                curve[k1].vertex,
                curve[k2].vertex,
            )
            < d * ddist(curve[k1].vertex, curve[k2].vertex) * COS179
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
        d = ddist(curve[k].vertex, curve[k1].vertex)
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
        res.pen += (d1 ** 2)
        k = k1

    # /* check corners */
    k = i
    while k != j:
        k1 = (k + 1) % n_of_segments
        t = tangent(p0, p1, p2, p3, curve[k].c[2], curve[k1].c[2])
        if t < -0.5:
            return 1
        pt = bezier(t, p0, p1, p2, p3)
        d = ddist(curve[k].c[2], curve[k1].c[2])
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
            res.pen += ((d1 - d2) ** 2)
        k = k1
    return 0


def _opticurve(curve: _Curve, opttolerance: float) -> int:
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

    convc = list()

    # /* pre-calculate convexity: +1 = right turn, -1 = left turn, 0 = corner */
    for i in range(n_of_segments):
        if curve[i].tag == POTRACE_CURVETO:
            convc.append(sign(
                dpara(
                    curve[(i - 1) % n_of_segments].vertex,
                    curve[i].vertex,
                    curve[(i + 1) % n_of_segments].vertex,
                )
            ))
        else:
            convc.append(0)

    # /* pre-calculate areas */
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
            if opti_penalty(curve, i, j % n_of_segments, o, opttolerance, convc, areac):
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
    for i in range(om):
        i1 = (i + 1) % om
        new_curve[i].beta = s[i] / (s[i] + t[i1])
    new_curve.alphacurve = True
    return 0


# /* ---------------------------------------------------------------------- */


def process_path(
    plist: list,
    alphamax=1.0,
    opticurve=True,
    opttolerance=0.2,
) -> int:
    """/* return 0 on success, 1 on error with errno set. */"""

    def TRY(x):
        if x:
            raise ValueError

    # /* call downstream function with each path */
    for p in plist:
        TRY(_calc_sums(p))
        TRY(_calc_lon(p))
        TRY(_bestpolygon(p))
        TRY(_adjust_vertices(p))
        if not p.sign:  # /* reverse orientation of negative paths */
            reverse(p._curve)
        _smooth(p._curve, alphamax)
        if opticurve:
            TRY(_opticurve(p, opttolerance))
            p._fcurve = p._ocurve
        else:
            p._fcurve = p._curve
    return 0