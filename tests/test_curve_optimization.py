import pytest
from vectorvision.curve_optimization import *
from vectorvision.vertex_adjustment import _Curve


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


def test_calculate_alpha():
    assert calculate_alpha(10.813, 188.035) == pytest.approx(0.0485093)


@pytest.fixture
def curve1():
    curve = _Curve(3)
    curve[0].c[0] = (40.725, 15.3375)
    curve[0].c[1] = (40.725, 14.8875)
    curve[0].c[2] = (41.0, 14.75)
    curve[0].vertex = (40.5, 15.0)
    curve[0].tag = 1

    curve[1].c[0] = (41.275, 14.6125)
    curve[1].c[1] = (41.5, 14.95)
    curve[1].c[2] = (41.5, 15.5)
    curve[1].vertex = (41.5, 14.5)
    curve[1].tag = 1

    curve[2].c[0] = (41.5, 16.05)
    curve[2].c[1] = (41.275, 16.1625)
    curve[2].c[2] = (41.0, 15.75)
    curve[2].vertex = (41.5, 16.5)
    curve[2].tag = 1
    return curve


@pytest.fixture
def curve2():
    curve = _Curve(6)
    curve[0].c[0] = (36.0613, 31.6005)
    curve[0].c[1] = (36.9856, 29.5071)
    curve[0].c[2] = (37.20653, 29.39673)
    curve[0].vertex = (36.80497, 29.59751)
    curve[0].tag = 1

    curve[1].c[0] = (37.42738, 29.28630)
    curve[1].c[1] = (37.78158, 29.33056)
    curve[1].c[2] = (37.99365, 29.49507)
    curve[1].vertex = (37.60808, 29.19595)
    curve[1].tag = 1

    curve[2].c[0] = (38.20571, 29.65958)
    curve[2].c[1] = (37.51433, 32.99049)
    curve[2].c[2] = (36.45725, 36.89709)
    curve[2].vertex = (38.37921, 29.79419)
    curve[2].tag = 1

    curve[3].c[0] = (35.18430, 41.60149)
    curve[3].c[1] = (34.03970, 44)
    curve[3].c[2] = (33.06764, 44)
    curve[3].vertex = (34.53529, 44)
    curve[3].tag = 1

    curve[4].c[0] = (31.90294, 44)
    curve[4].c[1] = (31.79609, 43.43236)
    curve[4].c[2] = (32.55, 41.25)
    curve[4].vertex = (31.6, 44)
    curve[4].tag = 1

    curve[5].c[0] = (33.072500000000005, 39.7375)
    curve[5].c[1] = (34.24362, 36.49693)
    curve[5].c[2] = (35.15249, 34.04875)
    curve[5].vertex = (33.5, 38.5)
    curve[5].tag = 1

    return curve


@pytest.fixture
def curve_different_convexity():
    curve = _Curve(4)
    curve[0].c[0] = (-0.12159090909090886, 1.2454545454545447)
    curve[0].c[1] = (-0.1233695652173914, 0.7554347826086949)
    curve[0].c[2] = (0.3369565217391305, 0.45652173913043437)
    curve[0].vertex = (-0.5, 1)
    curve[0].tag = 1

    curve[1].c[0] = (0.7972826086956524, 0.15760869565217372)
    curve[1].c[1] = (1.9222826086956522, 0.07871259175607004)
    curve[1].c[2] = (2.836956521739131, 0.28119706380575965)
    curve[1].vertex = (1.173913043478261, -0.08695652173913049)
    curve[1].tag = 1

    curve[2].c[0] = (4.384723251129528, 0.6238314437607854)
    curve[2].c[1] = (4.3849972303306455, 0.6993127136688428)
    curve[2].c[2] = (2.8409090909090917, 1.3701298701298705)
    curve[2].vertex = (4.5, 0.6493506493506498)
    curve[2].tag = 1

    curve[3].c[0] = (1.928409090909092, 1.7665584415584419)
    curve[3].c[1] = (0.8034090909090923, 1.8454545454545457)
    curve[3].c[2] = (0.3409090909090917, 1.5454545454545452)
    curve[3].vertex = (1.1818181818181834, 2.0909090909090913)
    curve[3].tag = 1

    return curve


def test_calculate_curve_area(curve1):
    assert calculate_curve_area(curve1, 0, 2) == 0.25


def test_precalculate_convexity1(curve1):
    assert precalculate_convexity(curve1) == [1, 1, 1]


def test_precalculate_areas(curve1):
    assert precalculate_areas(curve1) == [0.0, 0.25, 0.5, 0.25]


def test_check_check_if_smaller_than_179(curve1):
    assert check_if_smaller_than_179(curve1, 1, 0) is True


def test_check_check_if_same_convexity2(curve_different_convexity):
    precalculated = precalculate_convexity(curve_different_convexity)
    check_if_same_convexity(curve_different_convexity, 1, precalculated, 1, 0) is False


def test_check_check_if_same_convexity(curve1):
    precalculated = precalculate_convexity(curve1)
    assert check_if_same_convexity(curve1, 1, precalculated, 0, 1) is True


def test_check_necessary_condtition(curve1):
    assert check_necessary_conditions(curve1, 0, 2) is False


def test_optimize_no_optimization(curve1):
    assert optimize_curve(curve1, 0.2)[0].c == curve1[1].c
    assert optimize_curve(curve1, 0.2)[1].c == curve1[2].c
    assert optimize_curve(curve1, 0.2)[2].c == curve1[0].c


def test_caluclate_penalty(curve2):
    opti_t = calculate_optimization_penalty(curve2, 1, 3, 0.2)

    assert opti_t.pen == pytest.approx(0.091065)
    assert opti_t.s == pytest.approx(16.09551)
    assert opti_t.alpha == pytest.approx(0.03478198)


def test_optimize_true_optimization(curve2):
    opti_curve = optimize_curve(curve2, 0.2)

    assert len(opti_curve) == 4
    assert opti_curve[0].c[0][0] == pytest.approx(37.42738)
    assert opti_curve[0].c[1][0] == pytest.approx(37.78158)
    assert opti_curve[0].c[2][0] == pytest.approx(37.99365)
    assert opti_curve[1].c[0][0] == pytest.approx(38.64396)
    assert opti_curve[1].c[1][0] == pytest.approx(33.88929)
    assert opti_curve[1].c[2][0] == pytest.approx(33.06764)
    assert opti_curve[2].c[0][0] == pytest.approx(31.90294)
    assert opti_curve[2].c[1][0] == pytest.approx(31.79609)
    assert opti_curve[2].c[2][0] == pytest.approx(32.55)
    assert opti_curve[3].c[0][0] == pytest.approx(34.07131)
    assert opti_curve[3].c[1][0] == pytest.approx(36.94680)
    assert opti_curve[3].c[2][0] == pytest.approx(37.20653)

    assert opti_curve[0].c[0][1] == pytest.approx(29.28630)
    assert opti_curve[0].c[1][1] == pytest.approx(29.33056)
    assert opti_curve[0].c[2][1] == pytest.approx(29.49507)
    assert opti_curve[1].c[0][1] == pytest.approx(29.99957)
    assert opti_curve[1].c[1][1] == pytest.approx(44)
    assert opti_curve[1].c[2][1] == pytest.approx(44)
    assert opti_curve[2].c[0][1] == pytest.approx(44)
    assert opti_curve[2].c[1][1] == pytest.approx(43.432364)
    assert opti_curve[2].c[2][1] == pytest.approx(41.25)
    assert opti_curve[3].c[0][1] == pytest.approx(36.846204)
    assert opti_curve[3].c[1][1] == pytest.approx(29.526598)
    assert opti_curve[3].c[2][1] == pytest.approx(29.396734)
