from src.vertex_adjustment import calculate_intersection_point, find_closest_point_in_boundary
from src.vertex_adjustment import fit_least_squares, adjust_vertices
import pytest


def test_fit_least_squares():
    a, b = fit_least_squares([(1.3, 5), (4.5, 6), (6.5, 8), (10, 4)])
    assert a == pytest.approx(-0.06835, abs=1e-5)
    assert b == pytest.approx(6.13106, abs=1e-5)


def test_calculate_intersection_point1():
    assert calculate_intersection_point((3, 2), (2, -1)) == (-3, -7)


def test_calculate_intersection_point2():
    assert calculate_intersection_point((-6, 0), (-10, -3)) == (-0.75, 4.5)


def test_find_closest_point_in_boundary_point_in_boundary1():
    point = find_closest_point_in_boundary((3.56, 4.07), (4, 4), 0.5)
    x = point.x
    y = point.y
    assert (x, y) == (3.56, 4.07)


def test_find_closest_point_in_boundary_point_in_boundary2():
    point = find_closest_point_in_boundary((6.78, 9.16), (6, 9), 1)
    x = point.x
    y = point.y
    assert (x, y) == (6.78, 9.16)


def test_find_closest_point_in_boundary_point_outside_boundary1():
    point = find_closest_point_in_boundary((6.78, 4), (4, 4), 0.5)
    x = point.x
    y = point.y
    assert (x, y) == (4.5, 4)


def test_find_closest_point_in_boundary_point_outside_boundary2():
    point = find_closest_point_in_boundary((4.25, 0.4), (4, 4), 0.5)
    x = point.x
    y = point.y
    assert (x, y) == (4.25, 3.5)


def test_find_closest_point_in_boundary_point_in_boundary3():
    point = find_closest_point_in_boundary((6.78, 9.16), (5, 5), 0.5)
    x = point.x
    y = point.y
    assert (x, y) == (5.5, 5.5)


def test_adjust_vertices():
    curves = adjust_vertices([(0, 0), (5, 6), (8, 13), (10, 15), (10, 8), (9, 0), (9, -3), (8, -7), (6, -4), (3, -2)],
                             [0, 3, 7])
    assert len(curves) == 3
    assert curves[0].vertex[0] == 9.5
    assert curves[0].vertex[1] == 14.5
    assert curves[1].vertex[0] == 0.5
    assert curves[1].vertex[1] == 0.5
    assert curves[2].vertex[0] == 8.259365994236312
    assert curves[2].vertex[1] == -6.604775627830384