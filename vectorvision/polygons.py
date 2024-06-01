import math
import numpy as np
from collections import namedtuple


Sums = namedtuple(
    "Sums", ["x", "y", "xy", "x2", "y2"], defaults=[0.0, 0.0, 0.0, 0.0, 0.0]
)


def calc_sums(path: list) -> namedtuple:
    """
    Calculate cumulative sums for the given path.

    Args:
        path (list): A list of tuples, where each tuple represents a point (x, y).

    Returns:
        sums (Sums): A list of `Sums` namedtuples, each containing cumulative sums of x, y, xy, x^2, and y^2 coordinates.
    """

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


def cyclic(a: int, b: int, c: int) -> bool:
    """
    Determine if the value 'b' is between 'a' and 'c' in a cyclic sense.

    Args:
        a (int): The start value.
        b (int): The value to check.
        c (int): The end value.

    Returns:
        bool: True if a <= b < c in a cyclic sense (mod n), False otherwise.
    """
    if a <= c:
        return a <= b < c
    else:
        return a <= b or b < c


def get_next_corners(path: list, path_len: int) -> list:
    """
    Return the list of indices of the next corner for each point in the path.
    A corner is defined as a point where the direction changes.

    Args:
        path (list): A list of tuples representing points in the path.
        path_len (int): The length of the path.

    Returns:
        list: A list of indices of the next corner for each point in the path.
    """
    current_corner_index = 0
    next_corner = [None] * path_len

    for i in range(path_len - 1, -1, -1):
        if (
            path[i][0] != path[current_corner_index][0]
            and path[i][1] != path[current_corner_index][1]
        ):
            current_corner_index = i + 1

        next_corner[i] = current_corner_index

    return next_corner


def compute_direction(point1: tuple, point2: tuple) -> int:
    """
    Compute the path direction between two points.

    Args:
        point1 (tuple): The coordinates of the first point (x, y).
        point2 (tuple): The coordinates of the second point (x, y).

    Returns:
        int: The index representing the direction:
             (0, 1)[N] == 2, (1, 0)[E] == 3, (0, -1)[S] == 1, (-1, 0)[W] == 0.
    """
    distance_x = point2[0] - point1[0]
    distance_y = point2[1] - point1[1]

    return (3 + 3 * np.sign(distance_x) + np.sign(distance_y)) // 2


def compute_vector(point1: tuple, point2: tuple) -> tuple:
    """
    Compute the vector between two points.

    Args:
        point1 (tuple): The coordinates of the first point (x, y).
        point2 (tuple): The coordinates of the second point (x, y).

    Returns:
        tuple: A tuple representing the vector (dx, dy) between the points.
    """
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]
    return [x, y]


def vector_is_not_between(
    vector: list, right_constraint: list, left_constraint: list
) -> bool:
    """
    Check if the vector is kept between two constraining vectors.

    Args:
        vector (list): The vector to be checked.
        right_constraint (list): The right constraint vector.
        left_constraint (list): The left constraint vector.

    Returns:
        bool: True if the vector is not between the two constraints, False otherwise.
    """
    return (
        np.cross(right_constraint, vector) < 0 or np.cross(left_constraint, vector) > 0
    )


def get_pivot_points(path: list, next_corner: list, path_len: int) -> list:
    """
    Calculate the pivot points for each point in the path.

    For each index i, the pivot point k is the furthest point forming a straight path between them, such that:
    all of the points j within i < j < k lie on a line connecting i, k.

    Args:
        path (list): The list of points representing the path.
        next_corner (list): The list of indices of the next corner for each point in the path.
        path_len (int): The length of the path.

    Returns:
        list: A list of indexes of pivot points for each point of the path.
    """
    # Counter of the occured directions in a format: [W, S, N, E]
    direction_counter = [0, 0, 0, 0]
    pivot_points = [None] * path_len

    for i in range(path_len - 1, -1, -1):

        direction_counter[:] = [0, 0, 0, 0]
        direction = compute_direction(path[i], path[(i + 1) % path_len])
        direction_counter[direction] += 1

        right_constraint = [0, 0]
        left_constraint = [0, 0]

        next_corner_index = next_corner[i]
        last_corner_index = i

        subpath_vector = compute_vector(path[i], path[next_corner_index])
        direction = compute_direction(path[last_corner_index], path[next_corner_index])
        direction_counter[direction] += 1

        # find the last corner that is laying on the straight subpath
        # next_corner_index is the first corner that violates the constraints
        while not (
            all(direction_counter)
            or vector_is_not_between(subpath_vector, right_constraint, left_constraint)
        ):

            if abs(subpath_vector[0]) > 1 or abs(subpath_vector[1]) > 1:
                off_x = subpath_vector[0] + (
                    1
                    if (
                        subpath_vector[1] >= 0
                        and (subpath_vector[1] > 0 or subpath_vector[0] < 0)
                    )
                    else -1
                )
                off_y = subpath_vector[1] + (
                    1
                    if (
                        subpath_vector[0] <= 0
                        and (subpath_vector[0] < 0 or subpath_vector[1] < 0)
                    )
                    else -1
                )
                if np.cross(right_constraint, [off_x, off_y]) >= 0:
                    right_constraint[0] = off_x
                    right_constraint[1] = off_y
                off_x = subpath_vector[0] + (
                    1
                    if (
                        subpath_vector[1] <= 0
                        and (subpath_vector[1] < 0 or subpath_vector[0] < 0)
                    )
                    else -1
                )
                off_y = subpath_vector[1] + (
                    1
                    if (
                        subpath_vector[0] >= 0
                        and (subpath_vector[0] > 0 or subpath_vector[1] < 0)
                    )
                    else -1
                )
                if np.cross(left_constraint, [off_x, off_y]) <= 0:
                    left_constraint[0] = off_x
                    left_constraint[1] = off_y

            last_corner_index = next_corner_index
            next_corner_index = next_corner[last_corner_index]
            subpath_vector = compute_vector(path[i], path[next_corner_index])
            direction = compute_direction(
                path[last_corner_index], path[next_corner_index]
            )
            direction_counter[direction] += 1

            if not cyclic(next_corner_index, i, last_corner_index):
                break

        x_direction = np.sign(path[next_corner_index][0] - path[last_corner_index][0])
        y_direction = np.sign(path[next_corner_index][1] - path[last_corner_index][1])
        subpath_vector = compute_vector(path[i], path[last_corner_index])
        direction_vector = (x_direction, y_direction)

        # Once we have those 2 corners we can calculate the pivot point
        # between them that forms a straight subpath from the starting point i

        # The vector of the desired subpath can be described as:
        #   V = (vector from i to last_corner_index) + (j * direction vector)
        #   Where the value j is the distance from the pivot_index to the last point
        # We're looking for a vector V that is containted between the L&R constraints
        # So that:
        #   np.cross(right_constraint, subpath_vector + pivot_point * direction_vector) >= 0
        #   np.cross(left_constraint, subpath_vector + pivot_point * direction_vector) <= 0
        # The final pivot point = (last_corner_index + j) % path_len
        # And the value j can be calculated from the bilinearity of the cross product as:

        a = np.cross(right_constraint, subpath_vector)
        b = np.cross(right_constraint, direction_vector)

        c = np.cross(left_constraint, subpath_vector)
        d = np.cross(left_constraint, direction_vector)

        if b < 0:
            j = a // -b
        elif d > 0:
            j = min(path_len, (-c // d))
        else:
            j = path_len

        pivot_points[i] = (last_corner_index + j) % path_len

    return pivot_points


def get_longest_straight_subpaths(path: list) -> list:
    """
    Return a list of indexes forming the longest straight subpaths in the given path.

    Args:
        path (list): A list of points representing the path.

    Returns:
        list: A list of point indexes forming the longest straight subpaths.
    """
    path_len = len(path)
    longest_straight_subpaths = [None] * path_len

    next_corner = get_next_corners(path, path_len)
    pivot_point = get_pivot_points(path, next_corner, path_len)

    # Remove the cyclic inaccuracies so that longest_straight_subpaths[i]
    # represents the largest k such that for all i' with i <= i' < k, i' < k <= pivot_point[i'].

    j = pivot_point[path_len - 1]
    longest_straight_subpaths[path_len - 1] = j
    for i in range(path_len - 1, -1, -1):
        if cyclic(i + 1, pivot_point[i], j):
            j = pivot_point[i]
        longest_straight_subpaths[i] = j

    return longest_straight_subpaths


def penalty3(path: list, sums: list, i: int, j: int) -> float:
    """
    Calculate the penalty of an edge from point i to point j in the given path.

    Args:
        path (list): List of points representing the path.
        sums (list): List of precomputed sums used for penalty calculations.
        i (int): Starting point index.
        j (int): Ending point index.

    Returns:
        float: Penalty value.
    """
    path_len = len(path)

    rotations = 0
    if j >= path_len:
        j -= path_len
        rotations = 1

    if rotations == 0:
        segment_sum_x = sums[j + 1].x - sums[i].x
        segment_sum_y = sums[j + 1].y - sums[i].y
        segment_sum_x2 = sums[j + 1].x2 - sums[i].x2
        segment_sum_xy = sums[j + 1].xy - sums[i].xy
        segment_sum_y2 = sums[j + 1].y2 - sums[i].y2
        k = j + 1 - i
    else:
        segment_sum_x = sums[j + 1].x - sums[i].x + sums[path_len].x
        segment_sum_y = sums[j + 1].y - sums[i].y + sums[path_len].y
        segment_sum_x2 = sums[j + 1].x2 - sums[i].x2 + sums[path_len].x2
        segment_sum_xy = sums[j + 1].xy - sums[i].xy + sums[path_len].xy
        segment_sum_y2 = sums[j + 1].y2 - sums[i].y2 + sums[path_len].y2
        k = j + 1 - i + path_len

    mid_x = (path[i][0] + path[j][0]) / 2.0 - path[0][0]
    mid_y = (path[i][1] + path[j][1]) / 2.0 - path[0][1]
    edge_y = path[j][0] - path[i][0]
    edge_x = -(path[j][1] - path[i][1])

    # Calculate the componenets of the Penalty equation from the paper
    a = (segment_sum_x2 - 2 * segment_sum_x * mid_x) / k + mid_x * mid_x
    b = (
        segment_sum_xy - segment_sum_x * mid_y - segment_sum_y * mid_x
    ) / k + mid_x * mid_y
    c = (segment_sum_y2 - 2 * segment_sum_y * mid_y) / k + mid_y * mid_y

    penalty = math.sqrt(
        edge_x * edge_x * a + 2 * edge_x * edge_y * b + edge_y * edge_y * c
    )

    return penalty


def clip_path_forward(longest_straight_subpaths: list, path_len: int) -> list:
    """
    Calculate the forward clipping path.

    Args:
        longest_straight_subpaths (list): List of point indexes forming the longest straight subpaths.
        path_len (int): Length of the path.

    Returns:
        list: Forward clipping path.
    """
    forward_clips = [None] * path_len

    for i in range(path_len):
        c = (longest_straight_subpaths[(i - 1) % path_len] - 1) % path_len
        if c == i:
            c = (i + 1) % path_len
        if c < i:
            forward_clips[i] = path_len
        else:
            forward_clips[i] = c

    return forward_clips


def clip_path_backward(forward_clips: list, path_len: int) -> list:
    """
    Calculate the backward clipping path, non-cyclic.

    Args:
        forward_clips (list): Forward clipping path.
        path_len (int): Length of the path.

    Returns:
        list: Backward clipping path.
    """

    backward_clips = [None] * (path_len + 1)

    j = 1
    for i in range(path_len):
        while j <= forward_clips[i]:
            backward_clips[j] = i
            j += 1

    return backward_clips


def get_segment_bounds_forward(forward_clips: list, path_len: int) -> tuple:
    """
    Calculate the forward segment bounds.

    Args:
        forward_clips (list): Forward clipping path.
        path_len (int): Length of the path.

    Returns:
        tuple: A tuple containing the number of segments and the forward segment bounds.
    """
    seg_bounds_F = [None] * (path_len + 1)
    i = 0
    j = 0
    while i < path_len:
        seg_bounds_F[j] = i
        i = forward_clips[i]
        j += 1
    seg_bounds_F[j] = path_len
    segment_num = j

    return segment_num, seg_bounds_F


def get_segment_bounds_backward(
    backward_clips: list, segment_num: int, path_len: int
) -> list:
    """
    Calculate the backward segment bounds.

    Args:
        backward_clips (list): Backward clipping path.
        segment_num (int): Number of segments.
        path_len (int): Length of the path.

    Returns:
        list: Backward segment bounds.
    """
    seg_bounds_B = [None] * (path_len + 1)
    i = path_len

    for j in range(segment_num, 0, -1):
        seg_bounds_B[j] = i
        i = backward_clips[i]
    seg_bounds_B[0] = 0

    return seg_bounds_B


def get_best_polygon(path: list) -> list:
    """
    Find the optimal polygon for the given path.
    This function fills in the m and po components and returns the optimal polygon.
    Assumes i=0 is in the polygon. This is a non-cyclic version.

    Args:
        path (list): List of points representing the path.

    Returns:
        list: Optimal polygon as a list of point indices.
    """

    path_len = len(path)
    sums = calc_sums(path)
    longest_straight_subpaths = get_longest_straight_subpaths(path)

    penalties = [None] * (path_len + 1)
    best_path_vector = [None] * (path_len + 1)

    forward_clips = clip_path_forward(
        longest_straight_subpaths, path_len
    )  # longest segment pointer, non-cyclic
    backward_clips = clip_path_backward(
        forward_clips, path_len
    )  # backwards segment pointer, non-cyclic

    segments_num, seg_bounds_F = get_segment_bounds_forward(
        forward_clips, path_len
    )  # forward segment bounds
    seg_bounds_B = get_segment_bounds_backward(
        backward_clips, segments_num, path_len
    )  # backward segment bounds

    penalties[0] = 0
    for j in range(1, segments_num + 1):
        for i in range(seg_bounds_B[j], seg_bounds_F[j] + 1):
            best = -1
            for k in range(seg_bounds_F[j - 1], backward_clips[i] - 1, -1):
                thispen = penalty3(path, sums, k, i) + penalties[k]
                if best < 0 or thispen < best:
                    best_path_vector[i] = k
                    best = thispen
            penalties[i] = best

    polygon = [None] * segments_num

    # Save the best polygon path from the best_path_vector
    i = path_len
    j = segments_num - 1
    while i > 0:
        i = best_path_vector[i]
        polygon[j] = i
        j -= 1

    return polygon
