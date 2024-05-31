import math
import numpy as np
from collections import namedtuple


Sums = namedtuple(
    "Sums", ["x", "y", "xy", "x2", "y2"], defaults=[0.0, 0.0, 0.0, 0.0, 0.0]
)


def calc_sums(path) -> int:
    a = np.array([(0, 0)] + path)
    a[1:, :] -= np.array(path[0])
    css = np.cumsum(a, axis=0)
    cs2 = np.cumsum(np.power(a, 2), axis=0)
    csm = np.cumsum(a[:, 0] * a[:, 1])

    sums = []
    for i in range(len(path) + 1):
        x, y = css[i]
        x2, y2 = cs2[i]
        sums.append(Sums(x, y, csm[i], x2, y2))
    return sums


def xprod(p1x, p1y, p2x, p2y) -> float:
    """calculate p1 x p2"""
    return p1x * p2y - p1y * p2x


def cyclic(a: int, b: int, c: int) -> int:
    """
    /* return 1 if a <= b < c < a, in a cyclic sense (mod n) */
    """
    if a <= c:
        return a <= b < c
    else:
        return a <= b or b < c


def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    else:
        return 0


def mod(a: int, n: int) -> int:
    """Note: the "mod" macro works correctly for
    negative a. Also note that the test for a>=n, while redundant,
    speeds up the mod function by 70% in the average case (significant
    since the program spends about 16% of its time here - or 40%
    without the test)."""
    return a % n


def floordiv(a: int, n: int):
    """
    The "floordiv" macro returns the largest integer <= a/n,
    and again this works correctly for negative a, as long as
    a,n are integers and n>0.
    """
    return a // n


def calc_longest_straight_subpaths(path):
    path_len = len(path)
    direction_counter = [0, 0, 0, 0]
    pivk = [None] * path_len  # pivk[n]
    next_corner = [None] * path_len  # nc[n]: next corner

    curr_corner_index = 0
    for i in range(path_len - 1, -1, -1):
        if (
            path[i][0] != path[curr_corner_index][0]
            and path[i][1] != path[curr_corner_index][1]
        ):
            curr_corner_index = i + 1  # /* necessarily i<n-1 in this case */
        next_corner[i] = curr_corner_index

    longest_straight_subpaths = [None] * path_len

    # determine pivot points: for each i, let pivk[i] be the furthest k
    # such that all j with i<j<k lie on a line connecting i,k.

    for i in range(path_len - 1, -1, -1):

        direction_counter[0] = direction_counter[1] = direction_counter[2] = (
            direction_counter[3]
        ) = 0

        # keep track of "directions" that have occurred
        direction = (
            3
            + 3 * (path[mod(i + 1, path_len)][0] - path[i][0])
            + (path[mod(i + 1, path_len)][1] - path[i][1])
        ) // 2

        direction_counter[direction] += 1

        constraint0x = 0
        constraint0y = 0
        constraint1x = 0
        constraint1y = 0

        # find the next k such that no straight line from i to k
        curr_corner_index = next_corner[i]
        k1 = i
        while True:
            break_inner_loop_and_continue = False
            direction = (
                int(
                    3
                    + 3 * sign(path[curr_corner_index][0] - path[k1][0])
                    + sign(path[curr_corner_index][1] - path[k1][1])
                )
                // 2
            )
            direction_counter[direction] += 1

            # if all four "directions" have occurred, cut this path
            if (
                direction_counter[0]
                and direction_counter[1]
                and direction_counter[2]
                and direction_counter[3]
            ):
                pivk[i] = k1
                break_inner_loop_and_continue = True
                break  # goto foundk;

            cur_x = path[curr_corner_index][0] - path[i][0]
            cur_y = path[curr_corner_index][1] - path[i][1]

            if (
                xprod(constraint0x, constraint0y, cur_x, cur_y) < 0
                or xprod(constraint1x, constraint1y, cur_x, cur_y) > 0
            ):
                break

            # see if current constraint is violated
            # else, update constraint
            if abs(cur_x) <= 1 and abs(cur_y) <= 1:
                pass  # /* no constraint */
            else:
                off_x = cur_x + (1 if (cur_y >= 0 and (cur_y > 0 or cur_x < 0)) else -1)
                off_y = cur_y + (1 if (cur_x <= 0 and (cur_x < 0 or cur_y < 0)) else -1)
                if xprod(constraint0x, constraint0y, off_x, off_y) >= 0:
                    constraint0x = off_x
                    constraint0y = off_y
                off_x = cur_x + (1 if (cur_y <= 0 and (cur_y < 0 or cur_x < 0)) else -1)
                off_y = cur_y + (1 if (cur_x >= 0 and (cur_x > 0 or cur_y < 0)) else -1)
                if xprod(constraint1x, constraint1y, off_x, off_y) <= 0:
                    constraint1x = off_x
                    constraint1y = off_y
            k1 = curr_corner_index
            curr_corner_index = next_corner[k1]
            if not cyclic(curr_corner_index, i, k1):
                break
        if break_inner_loop_and_continue:
            # This previously was a goto to the end of the for i statement.
            continue
        # constraint_viol:
        """k1 was the last "corner" satisfying the current constraint, and
        k is the first one violating it. We now need to find the last
        point along k1..k which satisfied the constraint."""
        # dk: direction of k-k1
        dk_x = sign(path[curr_corner_index][0] - path[k1][0])
        dk_y = sign(path[curr_corner_index][1] - path[k1][1])
        cur_x = path[k1][0] - path[i][0]
        cur_y = path[k1][1] - path[i][1]
        """find largest integer j such that xprod(constraint[0], cur+j*dk) >= 0 
        and xprod(constraint[1], cur+j*dk) <= 0. Use bilinearity of xprod. */"""
        a = xprod(constraint0x, constraint0y, cur_x, cur_y)
        b = xprod(constraint0x, constraint0y, dk_x, dk_y)
        c = xprod(constraint1x, constraint1y, cur_x, cur_y)
        d = xprod(constraint1x, constraint1y, dk_x, dk_y)
        """find largest integer j such that a+j*b>=0 and c+j*d<=0. This
        can be solved with integer arithmetic."""
        j = float("inf")
        if b < 0:
            j = floordiv(a, -b)
        if d > 0:
            j = min(j, floordiv(-c, d))
        pivk[i] = mod(k1 + j, path_len)
        # foundk:
        # /* for i */

    """/* clean up: for each i, let lon[i] be the largest k such that for
         all i' with i<=i'<k, i'<k<=pivk[i']. */"""

    j = pivk[path_len - 1]
    longest_straight_subpaths[path_len - 1] = j
    for i in range(path_len - 2, -1, -1):
        if cyclic(i + 1, pivk[i], j):
            j = pivk[i]
        longest_straight_subpaths[i] = j

    i = path_len - 1
    while cyclic(mod(i + 1, path_len), j, longest_straight_subpaths[i]):
        longest_straight_subpaths[i] = j
        i -= 1

    return longest_straight_subpaths


if __name__ == "__main__":
    print(calc_longest_straight_subpaths([(0, 0), (1, 1), (2, 2), (3, 3)]))


def penalty3(path, sums, i: int, j: int) -> float:
    """Auxiliary function: calculate the penalty of an edge from i to j in
    the given path. This needs the "lon" and "sum*" data."""
    n = len(path)

    # /* assume 0<=i<j<=n    */

    r = 0  # /* rotations from i to j */
    if j >= n:
        j -= n
        r = 1

    # /* critical inner loop: the "if" gives a 4.6 percent speedup */
    if r == 0:
        x = sums[j + 1].x - sums[i].x
        y = sums[j + 1].y - sums[i].y
        x2 = sums[j + 1].x2 - sums[i].x2
        xy = sums[j + 1].xy - sums[i].xy
        y2 = sums[j + 1].y2 - sums[i].y2
        k = j + 1 - i
    else:
        x = sums[j + 1].x - sums[i].x + sums[n].x
        y = sums[j + 1].y - sums[i].y + sums[n].y
        x2 = sums[j + 1].x2 - sums[i].x2 + sums[n].x2
        xy = sums[j + 1].xy - sums[i].xy + sums[n].xy
        y2 = sums[j + 1].y2 - sums[i].y2 + sums[n].y2
        k = j + 1 - i + n

    px = (path[i][0] + path[j][0]) / 2.0 - path[0][0]
    py = (path[i][1] + path[j][1]) / 2.0 - path[0][1]
    ey = path[j][0] - path[i][0]
    ex = -(path[j][1] - path[i][1])

    a = (x2 - 2 * x * px) / k + px * px
    b = (xy - x * py - y * px) / k + px * py
    c = (y2 - 2 * y * py) / k + py * py

    s = ex * ex * a + 2 * ex * ey * b + ey * ey * c
    return math.sqrt(s)


def get_best_polygon(path) -> int:
    """
    /* find the optimal polygon. Fill in the m and po components. Return 1
         on failure with errno set, else 0. Non-cyclic version: assumes i=0
         is in the polygon. Fixme: implement cyclic version. */
    """
    path_length = len(path)
    sums = calc_sums(path)
    pen = [None] * (path_length + 1)  # /* pen[n+1]: penalty vector */
    prev = [None] * (path_length + 1)  # /* prev[n+1]: best path pointer vector */
    clip0 = [None] * path_length  # /* clip0[n]: longest segment pointer, non-cyclic */
    clip1 = [None] * (
        path_length + 1
    )  # /* clip1[n+1]: backwards segment pointer, non-cyclic */
    seg0 = [None] * (path_length + 1)  # /* seg0[m+1]: forward segment bounds, m<=n */
    seg1 = [None] * (path_length + 1)  # /* seg1[m+1]: backward segment bounds, m<=n */

    longest_straight_subpaths = calc_longest_straight_subpaths(path)
    # /* calculate clipped paths */
    for i in range(path_length):
        c = mod(longest_straight_subpaths[mod(i - 1, path_length)] - 1, path_length)
        if c == i:
            c = mod(i + 1, path_length)
        if c < i:
            clip0[i] = path_length
        else:
            clip0[i] = c

    # /* calculate backwards path clipping, non-cyclic. j <= clip0[i] iff
    # clip1[j] <= i, for i,j=0..n. */
    j = 1
    for i in range(path_length):
        while j <= clip0[i]:
            clip1[j] = i
            j += 1

    # calculate seg0[j] = longest path from 0 with j segments */
    i = 0
    j = 0
    while i < path_length:
        seg0[j] = i
        i = clip0[i]
        j += 1
    seg0[j] = path_length
    m = j

    # calculate seg1[j] = longest path to n with m-j segments */
    i = path_length
    for j in range(m, 0, -1):
        seg1[j] = i
        i = clip1[i]
    seg1[0] = 0

    """now find the shortest path with m segments, based on penalty3 */
    /* note: the outer 2 loops jointly have at most n iterations, thus
         the worst-case behavior here is quadratic. In practice, it is
         close to linear since the inner loop tends to be short. */
         """
    pen[0] = 0
    for j in range(1, m + 1):
        for i in range(seg1[j], seg0[j] + 1):
            best = -1
            for k in range(seg0[j - 1], clip1[i] - 1, -1):
                thispen = penalty3(path, sums, k, i) + pen[k]
                if best < 0 or thispen < best:
                    prev[i] = k
                    best = thispen
            pen[i] = best

    polygon = [None] * m

    # /* read off shortest path */
    i = path_length
    j = m - 1
    while i > 0:
        i = prev[i]
        polygon[j] = i
        j -= 1
    # print(polygon, m)
    return polygon
