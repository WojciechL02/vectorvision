from numpy.linalg import lstsq
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points


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


def fit_straight_line(points):
    x = np.array([point[0] for point in points])
    y = np.array([point[1] for point in points])
    A = np.vstack([x, np.ones(len(x))]).T
    return lstsq(A, y, rcond=None)[0]


def calculate_intersection_point(first_parameters, second_parameters):
    a, b = first_parameters
    c, d = second_parameters
    if a == c:
        return (0, 0)
    x_intersection = (d-b)/(a-c)
    y_intersection = x_intersection * a + b
    return (x_intersection, y_intersection)


def find_closest_point_in_boundary(original_point, boundary_center, boundary_manhatan_range):
    boundary_center_x, boundary_center_y = boundary_center
    poly = Polygon([(boundary_center_x+boundary_manhatan_range, boundary_center_y+boundary_manhatan_range),
                    (boundary_center_x-boundary_manhatan_range, boundary_center_y+boundary_manhatan_range),
                    (boundary_center_x+boundary_manhatan_range, boundary_center_y-boundary_manhatan_range),
                    (boundary_center_x-boundary_manhatan_range, boundary_center_y-boundary_manhatan_range)])
    point = Point(original_point)
    p1, p2 = nearest_points(poly, point)
    return p1


def adjust_vertices(path, polygon_points) -> int:
    """
    /* Adjust vertices of optimal polygon: calculate the intersection of
     the two "optimal" line segments, then move it into the unit square
     if it lies outside. Return 1 with errno set on error; 0 on
     success. */
    """
    curve = _Curve(len(polygon_points))

    points = path[polygon_points[-2]:polygon_points[-1]+1]
    prev_coeff = fit_straight_line(points)

    points = path[polygon_points[-1]:] + [path[polygon_points[0]]]
    coeffs = fit_straight_line(points)

    intersection_point = calculate_intersection_point(coeffs, prev_coeff)
    point_in_boundaries = find_closest_point_in_boundary(intersection_point, path[polygon_points[-1]], 0.5)

    curve[-1].vertex[0] = point_in_boundaries.x
    curve[-1].vertex[1] = point_in_boundaries.y
    prev_point_idx = polygon_points[0]
    prev_coeff = coeffs

    for i, polygon_point in enumerate(polygon_points[1:]):

        points = path[prev_point_idx:polygon_point+1]
        coeffs = fit_straight_line(points)

        intersection_point = calculate_intersection_point(coeffs, prev_coeff)
        point_in_boundaries = find_closest_point_in_boundary(intersection_point, path[polygon_point], 0.5)

        curve[i].vertex[0] = point_in_boundaries.x
        curve[i].vertex[1] = point_in_boundaries.y
        prev_point_idx = polygon_point
        prev_coeff = coeffs

    return curve
