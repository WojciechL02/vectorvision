import pytest
from src.curve_optimization import *


def test_calculate_distance_same_point():
    assert calculate_distance((2.37, 2.593), (2.37, 2.593)) == 0.0


def test_calculate_distance_same_x():
    p1 = (2.37, 2.593)
    p2 = (2.37, 4.2799)
    assert calculate_distance(p1, p2) == pytest.approx(1.6868999)


def test_calculate_distance_same_y():
    p1 = (3.37, 2.593)
    p2 = (8.2799, 2.593)
    assert calculate_distance(p1, p2) == pytest.approx(4.909899)


def test_dpara_rectangle():
    p1 = (0, 0)
    p2 = (0, 4)
    p3 = (8, 4)
    assert dpara(p1, p2, p3) == -32


def test_dpara_standard():
    p1 = (0, 0)
    p2 = (2, 4)
    p3 = (8, 4)
    assert dpara(p1, p2, p3) == -24


def test_dpara_positive():
    p1 = (0, 0)
    p2 = (0, -4)
    p3 = (8, -4)
    assert dpara(p1, p2, p3) == 32


def test_cprod_standard():
    p0 = (1, 3)
    p1 = (2, 4)
    p2 = (3.5, 2.37)
    p3 = (1.3, 9.49)
    assert cprod(p0, p1, p2, p3) == 9.32


def test_cprod_zeros():
    p0 = (0, 0)
    p1 = (0, 0)
    p2 = (0, 0)
    p3 = (0, 0)
    assert cprod(p0, p1, p2, p3) == 0.0


def test_iprod_three_points():
    assert iprod((0, 0), (1, 1), (2, 2)) == 4
    assert iprod((1, 1), (2, 2), (3, 3)) == 4
    assert iprod((0, 0), (2, 3), (4, 6)) == 26
    assert iprod((0, 0), (1, 2), (2, 4)) == 10


def test_iprod_four_points():
    assert iprod((0, 0), (1, 1), (2, 2), (3, 3)) == 2
    assert iprod((1, 1), (2, 2), (3, 3), (4, 4)) == 2
    assert iprod((0, 0), (2, 3), (4, 6), (6, 9)) == 13
    assert iprod((0, 0), (1, 2), (2, 4), (3, 6)) == 5


def test_iprod_mixed_signs():
    assert iprod((0, 0), (1, -1), (2, -2)) == 4
    assert iprod((0, 0), (-1, 1), (-2, 2)) == 4
    assert iprod((0, 0), (1, 1), (-1, -1)) == -2


def test_iprod_zero_vector():
    assert iprod((0, 0), (0, 0), (1, 1)) == 0
    assert iprod((0, 0), (1, 1), (0, 0)) == 0
    assert iprod((1, 1), (1, 1), (2, 2)) == 0
    assert iprod((0, 0), (1, 1), (2, 2), (2, 2)) == 0


def test_bezier_start():
    assert bezier(0, (0, 0), (1, 1), (2, 2), (3, 3)) == (0, 0)


def test_bezier_end():
    assert bezier(1, (0, 0), (1, 1), (2, 2), (3, 3)) == (3, 3)


def test_bezier_same_points():
    assert bezier(0.5, (1, 1), (1, 1), (1, 1), (1, 1)) == (1, 1)


def test_bezier_straight_line():
    assert bezier(0.5, (0, 0), (1, 1), (2, 2), (4, 4)) == (1.625, 1.625)


def test_bezier_known_case():
    assert bezier(0.5, (0, 0), (1, 2), (3, 3), (4, 0)) == (2.0, 1.875)


def test_tangent_no_solution():
    p0, p1, p2, p3 = (0, 0), (1, 1), (2, 2), (3, 3)
    q0, q1 = (0, 1), (1, 2)
    assert tangent(p0, p1, p2, p3, q0, q1) == -1


def test_tangent_two_solutions():
    p0, p1, p2, p3 = (0, 0), (0, 3), (3, 3), (3, 0)
    q0, q1 = (1, 1), (2, 2)
    t = tangent(p0, p1, p2, p3, q0, q1)
    assert 0 <= t <= 1


def test_tangent_control_point_match():
    p0, p1, p2, p3 = (0, 0), (2, 2), (3, 3), (3, 1.5)
    q0, q1 = (0, 1), (2, 2)
    t = tangent(p0, p1, p2, p3, q0, q1)
    assert t == pytest.approx(0.54858377)


def test_tangent_degenerate_case():
    p0, p1, p2, p3 = (0, 0), (0, 0), (0, 0), (0, 0)
    q0, q1 = (0, 1), (1, 2)
    assert tangent(p0, p1, p2, p3, q0, q1) == -1
