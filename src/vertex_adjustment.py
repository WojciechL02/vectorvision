import math
from vectorvision.src.polygons import mod, calc_sums


class _Curve:
    def __init__(self, m):
        self.segments = [_Segment() for _ in range(m)]
        self.alphacurve = False

    def __len__(self):
        return len(self.segments)

    @property
    def n(self):
        return len(self)

    def __getitem__(self, item):
        return self.segments[item]

class _Segment:
    def __init__(self):
        self.tag = 0
        self.c = [(0, 0), (0, 0), (0, 0)]
        self.vertex = [0, 0]
        self.alpha = 0.0
        self.alpha0 = 0.0
        self.beta = 0.0

def sq(x: float) -> float:
    return x * x

def pointslope(path, i: int, j: int, ctr, dir) -> None:
    """
    determine the center and slope of the line i..j. Assume i<j. Needs
    "sum" components of p to be set.
    """

    # /* assume i<j */

    n = len(path)
    sums = calc_sums(path)  # NEW sums was previously calculated in other place, should cache that result rather than recalculating

    r = 0  # /* rotations from i to j */

    while j >= n:
        j -= n
        r += 1

    while i >= n:
        i -= n
        r -= 1

    while j < 0:
        j += n
        r -= 1

    while i < 0:
        i += n
        r += 1

    x = sums[j + 1].x - sums[i].x + r * sums[n].x
    y = sums[j + 1].y - sums[i].y + r * sums[n].y
    x2 = sums[j + 1].x2 - sums[i].x2 + r * sums[n].x2
    xy = sums[j + 1].xy - sums[i].xy + r * sums[n].xy
    y2 = sums[j + 1].y2 - sums[i].y2 + r * sums[n].y2
    k = j + 1 - i + r * n

    ctr[0] = x / k
    ctr[1] = y / k

    a = float(x2 - x * x / k) / k
    b = float(xy - x * y / k) / k
    c = float(y2 - y * y / k) / k

    lambda2 = (
        a + c + math.sqrt((a - c) * (a - c) + 4 * b * b)
    ) / 2  # /* larger e.value */

    # /* now find e.vector for lambda2 */
    a -= lambda2
    c -= lambda2

    if math.fabs(a) >= math.fabs(c):
        l = math.sqrt(a * a + b * b)
        if l != 0:
            dir[0] = -b / l
            dir[1] = a / l
    else:
        l = math.sqrt(c * c + b * b)
        if l != 0:
            dir[0] = -c / l
            dir[1] = b / l
    if l == 0:
        # sometimes this can happen when k=4:
        # the two eigenvalues coincide */
        dir[0] = 0
        dir[1] = 0


"""
/* the type of (affine) quadratic forms, represented as symmetric 3x3
     matrices.    The value of the quadratic form at a vector (x,y) is v^t
     Q v, where v = (x,y,1)^t. */
"""


def quadform(Q: list, w) -> float:
    """Apply quadratic form Q to vector w = (w.x,w.y)"""
    v = (w.x[0], w.y[1], 1.0)
    sum = 0.0
    for i in range(3):
        for j in range(3):
            sum += v[i] * Q[i][j] * v[j]
    return sum

def adjust_vertices(path, polygon, m) -> int:
    """
    /* Adjust vertices of optimal polygon: calculate the intersection of
     the two "optimal" line segments, then move it into the unit square
     if it lies outside. Return 1 with errno set on error; 0 on
     success. */
    """
    path_len = len(path)
    x0 = path[0][0]
    y0 = path[0][1]

    ctr = [[0, 0] for i in range(m)]  # /* ctr[m] */
    dir = [[0, 0] for i in range(m)]  # /* dir[m] */
    q = [
        [[0.0 for a in range(3)] for b in range(3)] for c in range(m)
    ]  # quadform_t/* q[m] */
    v = [0.0, 0.0, 0.0]
    s = [0, 0]
    curve = _Curve(m)

    # /* calculate "optimal" point-slope representation for each line segment */
    for i in range(m):
        j = polygon[mod(i + 1, m)]
        j = mod(j - polygon[i], path_len) + polygon[i]
        pointslope(path, polygon[i], j, ctr[i], dir[i])

        # /* represent each line segment as a singular quadratic form;
        # the distance of a point (x,y) from the line segment will be
        # (x,y,1)Q(x,y,1)^t, where Q=q[i]. */
    for i in range(m):
        d = sq(dir[i][0]) + sq(dir[i][1])
        if d == 0.0:
            for j in range(3):
                for k in range(3):
                    q[i][j][k] = 0
        else:
            v[0] = dir[i][1]
            v[1] = -dir[i][0]
            v[2] = -v[1] * ctr[i][1] - v[0] * ctr[i][0]
            for l in range(3):
                for k in range(3):
                    q[i][l][k] = v[l] * v[k] / d

    """/* now calculate the "intersections" of consecutive segments.
         Instead of using the actual intersection, we find the point
         within a given unit square which minimizes the square distance to
         the two lines. */"""
    
    Q = [[0.0 for a in range(3)] for b in range(3)]
    for i in range(m):
        # double min, cand; #/* minimum and candidate for minimum of quad. form */
        # double xmin, ymin;	#/* coordinates of minimum */

        # /* let s be the vertex, in coordinates relative to x0/y0 */
        s[0] = path[polygon[i]][0] - x0
        s[1] = path[polygon[i]][1] - y0

        # /* intersect segments i-1 and i */

        j = mod(i - 1, m)

        # /* add quadratic forms */
        for l in range(3):
            for k in range(3):
                Q[l][k] = q[j][l][k] + q[i][l][k]

        while True:
            # /* minimize the quadratic form Q on the unit square */
            # /* find intersection */

            det = Q[0][0] * Q[1][1] - Q[0][1] * Q[1][0]
            w = None
            if det != 0.0:
                w = (
                    (-Q[0][2] * Q[1][1] + Q[1][2] * Q[0][1]) / det,
                    (Q[0][2] * Q[1][0] - Q[1][2] * Q[0][0]) / det,
                )
                break

            # /* matrix is singular - lines are parallel. Add another,
            # orthogonal axis, through the center of the unit square */
            if Q[0][0] > Q[1][1]:
                v[0] = -Q[0][1]
                v[1] = Q[0][0]
            elif Q[1][1]:
                v[0] = -Q[1][1]
                v[1] = Q[1][0]
            else:
                v[0] = 1
                v[1] = 0
            d = sq(v[0]) + sq(v[1])
            v[2] = -v[1] * s[1] - v[0] * s[0]
            for l in range(3):
                for k in range(3):
                    Q[l][k] += v[l] * v[k] / d
        dx = math.fabs(w[0] - s[0])
        dy = math.fabs(w[1] - s[1])
        if dx <= 0.5 and dy <= 0.5:
            curve[i].vertex[0] = w[0] + x0
            curve[i].vertex[1] = w[1] + y0
            continue

        # /* the minimum was not in the unit square; now minimize quadratic
        # on boundary of square */
        min = quadform(Q, s)
        xmin = s.x
        ymin = s.y

        if Q[0][0] != 0.0:
            for z in range(2):  # /* value of the y-coordinate */
                w.y = s.y - 0.5 + z
                w.x = -(Q[0][1] * w.y + Q[0][2]) / Q[0][0]
                dx = math.fabs(w.x - s.x)
                cand = quadform(Q, w)
                if dx <= 0.5 and cand < min:
                    min = cand
                    xmin = w.x
                    ymin = w.y
        if Q[1][1] != 0.0:
            for z in range(2):  # /* value of the x-coordinate */
                w.x = s.x - 0.5 + z
                w.y = -(Q[1][0] * w.x + Q[1][2]) / Q[1][1]
                dy = math.fabs(w.y - s.y)
                cand = quadform(Q, w)
                if dy <= 0.5 and cand < min:
                    min = cand
                    xmin = w.x
                    ymin = w.y
        # /* check four corners */
        for l in range(2):
            for k in range(2):
                w = (s.x - 0.5 + l, s.y - 0.5 + k)
                cand = quadform(Q, w)
                if cand < min:
                    min = cand
                    xmin = w.x
                    ymin = w.y
        curve[i].vertex.x = xmin + x0
        curve[i].vertex.y = ymin + y0
    
    return curve