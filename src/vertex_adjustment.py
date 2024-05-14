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


def adjust_vertices(path, polygon_points, m) -> int:
    """
    /* Adjust vertices of optimal polygon: calculate the intersection of
     the two "optimal" line segments, then move it into the unit square
     if it lies outside. Return 1 with errno set on error; 0 on
     success. */
    """
    curve = _Curve(m)
    # path = [path[0]] + path[1:]

    x = np.array([point[0] for point in path[polygon_points[-2]:polygon_points[-1]+1]])
    y = np.array([point[1] for point in path[polygon_points[-2]:polygon_points[-1]+1]])
    A = np.vstack([x, np.ones(len(x))]).T

    prev_coeff = lstsq(A, y, rcond=None)[0]

    x = np.array([point[0] for point in path[polygon_points[-1]:]] + [path[polygon_points[0]][0]])
    y = np.array([point[1] for point in path[polygon_points[-1]:]] + [path[polygon_points[0]][1]])
    A = np.vstack([x, np.ones(len(x))]).T

    a, b = lstsq(A, y, rcond=None)[0]
    c, d = prev_coeff

    x_intersection = (d-b)/(a-c)
    y_intersection = x_intersection * a + b

    point_x, point_y = path[polygon_points[-1]]
    poly = Polygon([(point_x+0.5, point_y+0.5), (point_x-0.5, point_y+0.5),
                    (point_x+0.5, point_y-0.5), (point_x-0.5, point_y-0.5)])
    point = Point(x_intersection, y_intersection)
    p1, p2 = nearest_points(poly, point)
    curve[-1].vertex[0] = p1.x
    curve[-1].vertex[1] = p1.y
    prev_point_idx = polygon_points[0]
    prev_coeff = (a, b)

    for i, polygon_point in enumerate(polygon_points[1:]):

        x = np.array([point[0] for point in path[prev_point_idx:polygon_point+1]])
        y = np.array([point[1] for point in path[prev_point_idx:polygon_point+1]])
        A = np.vstack([x, np.ones(len(x))]).T

        a, b = lstsq(A, y, rcond=None)[0]
        c, d = prev_coeff

        # print(i, prev_coeff, prev_point_idx, polygon_point, (a,b))
        x_intersection = (d-b)/(a-c)
        y_intersection = x_intersection * a + b

        # print(x_intersection, y_intersection, i)

        point_x, point_y = path[prev_point_idx]
        poly = Polygon([(point_x+0.5, point_y+0.5), (point_x-0.5, point_y+0.5),
                        (point_x+0.5, point_y-0.5), (point_x-0.5, point_y-0.5)])
        point = Point(x_intersection, y_intersection)
        p1, p2 = nearest_points(poly, point)

        curve[i].vertex[0] = p1.x
        curve[i].vertex[1] = p1.y

        prev_point_idx = polygon_point
        prev_coeff = (a, b)

    return curve
