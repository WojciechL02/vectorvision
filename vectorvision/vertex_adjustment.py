from numpy.linalg import lstsq
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from typing import Optional


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


def fit_least_squares(points: list[tuple[float, float]]) -> tuple[float, float]:
    """Fit linear function to given points in 2D with least squares method

    Args:
        points: list of points to which straight should be fitted

    Returns:
        Tuple (a, b) with parameters of fitted straight in format y=ax+b
    """

    x = np.array([point[0] for point in points])
    y = np.array([point[1] for point in points])
    A = np.vstack([x, np.ones(len(x))]).T
    return lstsq(A, y, rcond=None)[0]


def calculate_intersection_point(
    first_parameters: tuple[float, float], second_parameters: tuple[float, float]
) -> Optional[tuple[float, float]]:
    """Calculate point of intersection for two linear functions

    Args:
        first_parameters: Tuple (a, b), parameters of first straight in format ax+b
        second_parameters: Tuple (c, d), parameters of second straight in format cx+d

    Returns:
        Tuple (x, y) with point of intersection or None if straights are parallel
    """

    a, b = first_parameters
    c, d = second_parameters
    if a == c:
        return None
    x_intersection = (d - b) / (a - c)
    y_intersection = x_intersection * a + b
    return (x_intersection, y_intersection)


def find_closest_point_in_boundary(
    original_point: tuple[float, float],
    boundary_center: tuple[float, float],
    boundary_manhatan_range: float,
) -> Point:
    """Find point closest to original point but lying inside the square boundary around another point

    Args:
        original_point: location of original point
        boundary_center: center of boundary
        boundary_manhatan_range: distance along all main directions designating boundary location

    Returns:
        Point in boundary closest to original point
    """

    boundary_center_x, boundary_center_y = boundary_center
    poly = Polygon(
        [
            (
                boundary_center_x + boundary_manhatan_range,
                boundary_center_y + boundary_manhatan_range,
            ),
            (
                boundary_center_x - boundary_manhatan_range,
                boundary_center_y + boundary_manhatan_range,
            ),
            (
                boundary_center_x - boundary_manhatan_range,
                boundary_center_y - boundary_manhatan_range,
            ),
            (
                boundary_center_x + boundary_manhatan_range,
                boundary_center_y - boundary_manhatan_range,
            ),
        ]
    )
    point = Point(original_point)
    p1, _ = nearest_points(poly, point)
    return p1


def adjust_vertices(
    path: list[tuple[float, float]], polygon_points_idxs: list[int]
) -> _Curve:
    """
    Adjust vertices of optimal polygon: calculate the intersection of
     the two "optimal" line segments, then move it into the unit square
     if it lies outside.

        Args:
            path: list of points forming path
            polygon_points_idxs: list of points indexes in path contained in optimal polygon

        Returns:
            Curve representation of path
    """

    curve = _Curve(len(polygon_points_idxs))

    points = path[polygon_points_idxs[-2] : polygon_points_idxs[-1] + 1]
    prev_coeff = fit_least_squares(points)

    points = path[polygon_points_idxs[-1] :] + [path[polygon_points_idxs[0]]]
    coeffs = fit_least_squares(points)

    intersection_point = calculate_intersection_point(coeffs, prev_coeff)
    if intersection_point is None:
        intersection_point = (0, 0)

    point_in_boundaries = find_closest_point_in_boundary(
        intersection_point, path[polygon_points_idxs[-1]], 0.5
    )

    curve[-1].vertex[0] = point_in_boundaries.x
    curve[-1].vertex[1] = point_in_boundaries.y
    prev_point_idx = polygon_points_idxs[0]
    prev_coeff = coeffs

    for i, polygon_point in enumerate(polygon_points_idxs[1:]):

        points = path[prev_point_idx : polygon_point + 1]
        coeffs = fit_least_squares(points)

        intersection_point = calculate_intersection_point(coeffs, prev_coeff)
        if intersection_point is None:
            intersection_point = (0, 0)
        point_in_boundaries = find_closest_point_in_boundary(
            intersection_point, path[prev_point_idx], 0.5
        )

        curve[i].vertex[0] = point_in_boundaries.x
        curve[i].vertex[1] = point_in_boundaries.y
        prev_point_idx = polygon_point
        prev_coeff = coeffs

    return curve
