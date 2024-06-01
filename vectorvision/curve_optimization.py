from vectorvision.vertex_adjustment import _Curve
from vectorvision.utils import interval
from collections import namedtuple
import numpy as np
import math


OptiT = namedtuple("OptiT", ["pen", "c", "alpha", "s"])

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


def dpara(p0: tuple[float, float], p1, p2) -> float:
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


def bezier(t: float, p0, p1, p2, p3) -> tuple[float, float]:
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


def calculate_penalty_edges_tangency(
    curve: _Curve, start_index: int, end_index: int, opttolerance: float, p0, p1, p2, p3
) -> float:
    """Calculates part of penalty connected with tangency with edges

    Args:
        curve: curve for which subset we want to calculate penalty
        start_index: index of first segment of curve part for which we want to calculate penalty
        end_index: index of last segment of curve part for which we want to calculate penalty
        opttolerance: maximum deviation for which we will still perform replacing
        p0, p1, p2, p3: control points of new potential curve


    Returns:
        Value of the penalty
    """

    penalty = 0

    current_index = start_index
    while current_index != end_index:
        next_index = (current_index + 1) % curve.n
        t = tangent(
            p0, p1, p2, p3, curve[current_index].vertex, curve[next_index].vertex
        )
        if t < -0.5:
            return None
        pt = bezier(t, p0, p1, p2, p3)
        d = calculate_distance(curve[current_index].vertex, curve[next_index].vertex)
        if d == 0.0:  # /* this should never happen */
            return None
        d1 = dpara(curve[current_index].vertex, curve[next_index].vertex, pt) / d
        if math.fabs(d1) > opttolerance:
            return None
        if (
            iprod(curve[current_index].vertex, curve[next_index].vertex, pt) < 0
            or iprod(curve[next_index].vertex, curve[current_index].vertex, pt) < 0
        ):
            return 1
        penalty += d1**2
        current_index = next_index

    return penalty


def calculate_penalty_corners(
    curve, start_index, end_index, opttolerance, p0, p1, p2, p3
):
    """Calculates part of penalty connected with tangency with corners

    Args:
        curve: curve for which subset we want to calculate penalty
        start_index: index of first segment of curve part for which we want to calculate penalty
        end_index: index of last segment of curve part for which we want to calculate penalty
        opttolerance: maximum deviation for which we will still perform replacing
        p0, p1, p2, p3: control points of new potential curve

    Returns:
        Value of the penalty
    """

    penalty = 0

    current_index = start_index
    while current_index != end_index:
        next_index = (current_index + 1) % curve.n
        t = tangent(p0, p1, p2, p3, curve[current_index].c[2], curve[next_index].c[2])
        if t < -0.5:
            return None
        pt = bezier(t, p0, p1, p2, p3)
        d = calculate_distance(curve[current_index].c[2], curve[next_index].c[2])
        if d == 0.0:  # this should never happen
            return None
        d1 = dpara(curve[current_index].c[2], curve[next_index].c[2], pt) / d
        d2 = (
            dpara(
                curve[current_index].c[2],
                curve[next_index].c[2],
                curve[next_index].vertex,
            )
            / d
        )
        d2 *= 0.75 * curve[next_index].alpha
        if d2 < 0:
            d1 = -d1
            d2 = -d2
        if d1 < d2 - opttolerance:
            return None
        if d1 < d2:
            penalty += (d1 - d2) ** 2
        current_index = next_index

    return penalty


def check_if_smaller_than_179(curve, start_segment_idx, end_segment_idx):
    """Checks if condition of not exceeding 179 degrees in one curve is satisfied for given segments

    Args:
        curve: curve for which subset we want to perform check
        start_segment_idx: index of first segment of curve part for which we want to perform check
        end_segment_idx: index of last segment of curve part for which we want to perform check


    Returns:
        True if condition is satisfied, False otherwise
    """

    end_segment_plus_one_idx = (end_segment_idx + 1) % curve.n
    start_segment_plus_one_idx = (start_segment_idx + 1) % curve.n

    d = calculate_distance(
        curve[start_segment_idx].vertex, curve[start_segment_plus_one_idx].vertex
    )
    if (
        iprod(
            curve[start_segment_idx].vertex,
            curve[start_segment_plus_one_idx].vertex,
            curve[end_segment_idx].vertex,
            curve[end_segment_plus_one_idx].vertex,
        )
        < d
        * calculate_distance(
            curve[end_segment_idx].vertex, curve[end_segment_plus_one_idx].vertex
        )
        * COS179
    ):
        return False
    return True


def check_if_same_convexity(
    curve, convexity, convexity_precalculated, start_segment_idx, end_segment_idx
):
    """Checks if condition of the same convexity is satisfied for given segments

    Args:
        curve: curve for which subset we want to perform check
        convexity: expected convexity of segment
        convexity_precalculated: precalculated convexity to speed up calculations
        start_segment_idx: index of first segment of curve part for which we want to perform check
        end_segment_idx: index of last segment of curve part for which we want to perform check


    Returns:
        True if condition is satisfied, False otherwise
    """

    end_segment_idx_plus_one = (end_segment_idx + 1) % curve.n
    start_segment_plus_one_idx = (start_segment_idx + 1) % curve.n

    if convexity_precalculated[end_segment_idx] != convexity:
        return False
    if (
        np.sign(
            cprod(
                curve[start_segment_idx].vertex,
                curve[start_segment_plus_one_idx].vertex,
                curve[end_segment_idx].vertex,
                curve[end_segment_idx_plus_one].vertex,
            )
        )
        != convexity
    ):
        return False
    return True


def check_necessary_conditions(curve, start_segment_idx, end_segment_idx):
    """Checks if all necessary conditions to allow merging curves into one are satisfied

    Args:
        curve: curve for which subset we want to perform checks
        start_segment_idx: index of first segment of curve part for which we want to perform checks
        end_segment_idx: index of last segment of curve part for which we want to perform checks

    Returns:
        True if all conditions is satisfied, False otherwise
    """

    if (
        start_segment_idx == end_segment_idx
    ):  # sanity - a full loop can never be an opticurve
        return False

    current_segment = start_segment_idx
    next_segment = (current_segment + 1) % curve.n

    convexity_precalculated = precalculate_convexity(curve)
    convexity = convexity_precalculated[next_segment]

    if convexity == 0:  # there is corner here
        return False

    current_segment = next_segment
    while current_segment != end_segment_idx:
        next_segment = (current_segment + 1) % curve.n
        if not check_if_same_convexity(
            curve, convexity, convexity_precalculated, start_segment_idx, next_segment
        ):
            return False
        if not check_if_smaller_than_179(curve, start_segment_idx, next_segment):
            return False

        current_segment = next_segment

    return True


def calculate_curve_area(curve, start_segment_idx, end_segment_idx):
    """Calculate are under given segments of curve
    Args:
        curve: curve for which subset we want to calculate area
        start_segment_idx: index of first segment of curve part for which we want to calculate area
        end_segment_idx: index of last segment of curve part for which we want to calculate area


    Returns:
        Area under given segments of curve
    """

    precalculated_areas = precalculate_areas(curve)

    area = precalculated_areas[end_segment_idx] - precalculated_areas[start_segment_idx]
    area -= (
        dpara(
            curve[0].vertex, curve[start_segment_idx].c[2], curve[end_segment_idx].c[2]
        )
        / 2
    )
    if start_segment_idx >= end_segment_idx:
        area += precalculated_areas[curve.n]
    return area


def calculate_alpha(area, p0_o_p3_triangle_area):
    """Calculate alpha parameter for curve based on ratio of area under curve and triangle
      with two sides tangent to the curve
    Args:
        area: area under curve
        p0_o_p3_triangle_area: area of triangle

    Returns:
        Alpha parameter of curve
    """

    R = area / p0_o_p3_triangle_area  # relative area
    alpha = 2 - math.sqrt(4 - R / 0.3)  # overall alpha for p0-o-p3 curve

    return alpha


def calculate_optimization_penalty(
    curve: _Curve,
    start_segment_idx: int,
    end_segment_idx: int,
    opttolerance: float,
) -> int:
    """Calculate penalty of optimized curve part between two segments

    Args:
        curve: curve for which subset we want to calculate area
        start_segment_idx: index of first segment of curve part for which we want to calculate penalty
        end_segment_idx: index of last segment of curve part for which we want to calculate penalty
        opttolerance: maximum deviation for which we will still perform replacing

    Returns:
        Penalty of calculated optimal curve or None if cannot create optimal curve
        that will fit the requirements
    """

    n_of_segments = curve.n

    # check convexity, corner-freeness, and maximum bend < 179 degrees
    current_segment = start_segment_idx
    start_segment_plus_one_idx = (start_segment_idx + 1) % n_of_segments

    if not check_necessary_conditions(curve, start_segment_idx, end_segment_idx):
        return None

    # the curve we're working in:
    p0 = curve[start_segment_idx % n_of_segments].c[2]
    p1 = curve[start_segment_plus_one_idx].vertex
    p2 = curve[end_segment_idx % n_of_segments].vertex
    p3 = curve[end_segment_idx % n_of_segments].c[2]

    # determine its area
    area = calculate_curve_area(curve, start_segment_idx, end_segment_idx)

    # find intersection o of p0p1 and p2p3. Let t,s such that
    # o =interval(t,p0,p1) = interval(s,p3,p2). Let A be the area of the
    # triangle (p0,o,p3).

    A1 = dpara(p0, p1, p2)
    A2 = dpara(p0, p1, p3)
    A3 = dpara(p0, p2, p3)
    A4 = A1 + A3 - A2

    if A2 == A1:  # this should never happen
        return None

    t = A3 / (A3 - A4)
    s = A2 / (A2 - A1)
    A = A2 * t / 2.0

    if A == 0.0:  # this should never happen
        return None

    alpha = calculate_alpha(area, A)

    c = list()
    c.append(interval(t * alpha, p0, p1))
    c.append(interval(s * alpha, p3, p2))

    p1 = c[0]
    p2 = c[1]  # /* the proposed curve is now (p0,p1,p2,p3) */

    # calculate penalty
    # check tangency with edges
    current_segment = (start_segment_idx + 1) % n_of_segments
    pen_edges = calculate_penalty_edges_tangency(
        curve, current_segment, end_segment_idx, opttolerance, p0, p1, p2, p3
    )
    if pen_edges is None:
        return None

    # /* check corners */
    current_segment = start_segment_idx
    pen_corners = calculate_penalty_corners(
        curve, current_segment, end_segment_idx, opttolerance, p0, p1, p2, p3
    )
    if pen_corners is None:
        return None

    penalty = pen_edges + pen_corners

    return OptiT(penalty, c, alpha, s)


def precalculate_convexity(curve):
    """Precalculate convexity for curve
    Args:
        curve: curve to precalculate convexity

    Returns:
        Precalculated convexity for each segment of curve
    """

    convexity = list()

    # pre-calculate convexity: +1 = right turn, -1 = left turn, 0 = corner
    for i in range(curve.n):
        if curve[i].tag == POTRACE_CURVETO:
            convexity.append(
                np.sign(
                    dpara(
                        curve[(i - 1) % curve.n].vertex,
                        curve[i].vertex,
                        curve[(i + 1) % curve.n].vertex,
                    )
                )
            )
        else:
            convexity.append(0)

    return convexity


def precalculate_areas(curve):
    """Precalculate area for curve
    Args:
        curve: curve to precalculate area

    Returns:
        Precalculated area for each segment of curve
    """

    area = 0.0
    areac = [0.0]
    p0 = curve[0].vertex
    for i in range(curve.n):
        i1 = (i + 1) % curve.n
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
    """Optimize the path p, replacing sequences of Bezier segments by a
    single segment when possible.
    Args:
        curve: curve to optimize
        opttolerance: maximum deviation for which we will still perform replacing

    Returns:
        Optimized curve
    """
    n_of_segments = curve.n
    pt = [0] * (n_of_segments + 1)  # /* pt[m+1] */
    pen = [0.0] * (n_of_segments + 1)  # /* pen[m+1] */
    length = [0] * (n_of_segments + 1)  # /* len[m+1] */
    opt = [None] * (n_of_segments + 1)  # /* opt[m+1] */

    pt[0] = -1
    pen[0] = 0
    length[0] = 0

    for curr_last_segment in range(1, n_of_segments + 1):

        pt[curr_last_segment] = curr_last_segment - 1
        pen[curr_last_segment] = pen[curr_last_segment - 1]
        length[curr_last_segment] = length[curr_last_segment - 1] + 1
        for curr_start_segment in range(curr_last_segment - 2, -1, -1):
            opti_curve = calculate_optimization_penalty(
                curve,
                curr_start_segment,
                curr_last_segment % n_of_segments,
                opttolerance,
            )
            if opti_curve is None:
                break

            if length[curr_last_segment] > length[curr_start_segment] + 1 or (
                length[curr_last_segment] == length[curr_start_segment] + 1
                and pen[curr_last_segment] > pen[curr_start_segment] + opti_curve.pen
            ):
                opt[curr_last_segment] = opti_curve
                pt[curr_last_segment] = curr_start_segment
                pen[curr_last_segment] = pen[curr_start_segment] + opti_curve.pen
                length[curr_last_segment] = length[curr_start_segment] + 1
                opti_curve = None

    om = length[n_of_segments]
    new_curve = _Curve(om)

    curr_last_segment = n_of_segments
    for curr_start_segment in range(om - 1, -1, -1):
        if pt[curr_last_segment] == curr_last_segment - 1:
            new_curve[curr_start_segment].tag = curve[
                curr_last_segment % n_of_segments
            ].tag
            new_curve[curr_start_segment].c[0] = curve[
                curr_last_segment % n_of_segments
            ].c[0]
            new_curve[curr_start_segment].c[1] = curve[
                curr_last_segment % n_of_segments
            ].c[1]
            new_curve[curr_start_segment].c[2] = curve[
                curr_last_segment % n_of_segments
            ].c[2]
            new_curve[curr_start_segment].vertex = curve[
                curr_last_segment % n_of_segments
            ].vertex
            new_curve[curr_start_segment].alpha = curve[
                curr_last_segment % n_of_segments
            ].alpha
        else:
            new_curve[curr_start_segment].tag = POTRACE_CURVETO
            new_curve[curr_start_segment].c[0] = opt[curr_last_segment].c[0]
            new_curve[curr_start_segment].c[1] = opt[curr_last_segment].c[1]
            new_curve[curr_start_segment].c[2] = curve[
                curr_last_segment % n_of_segments
            ].c[2]
            new_curve[curr_start_segment].vertex = interval(
                opt[curr_last_segment].s,
                curve[curr_last_segment % n_of_segments].c[2],
                curve[curr_last_segment % n_of_segments].vertex,
            )
            new_curve[curr_start_segment].alpha = opt[curr_last_segment].alpha
        curr_last_segment = pt[curr_last_segment]

    return new_curve
