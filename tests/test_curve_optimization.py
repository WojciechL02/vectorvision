import pytest
from src.curve_optimization import *
from src.vertex_adjustment import _Curve


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
    curve[0].c[0] = (40.725, 15.337500000000006)
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
    curve[0].c[0] = (36.061358921161826, 31.60057053941909)
    curve[0].c[1] =  (36.98567747282985, 29.50716126358508)
    curve[0].c[2] =  (37.20653085248496, 29.396734573757527)
    curve[0].vertex = (36.80497925311203, 29.597510373443985)
    curve[0].tag = 1

    curve[1].c[0] = (37.427384232140064, 29.286307883929975)
    curve[1].c[1] = (37.78158820978288, 29.330560818800425)
    curve[1].c[2] =  (37.99365080280233, 29.495074429025195)
    curve[1].vertex = (37.60808245185788, 29.19595877407107)
    curve[1].tag = 1

    curve[2].c[0] = (38.205713395821775, 29.65958803924996)
    curve[2].c[1] = (37.51433602062434, 32.990497315083964)
    curve[2].c[2] = (36.45725663569692, 36.897095041989644)
    curve[2].vertex = (38.379219153746774, 29.794190083979316)
    curve[2].tag = 1

    curve[3].c[0] = (35.184301050119835, 41.60149611912235)
    curve[3].c[1] =  (34.03970010545675, 43.99999999999998)
    curve[3].c[2] =  (33.06764705882355, 43.99999999999997)
    curve[3].vertex = (34.53529411764707, 43.99999999999998)
    curve[3].tag = 1

    curve[4].c[0] = (31.902941176470623, 43.99999999999997)
    curve[4].c[1] = (31.796092184368767, 43.43236472945888)
    curve[4].c[2] =  (32.55000000000001, 41.249999999999986)
    curve[4].vertex = (31.60000000000003, 43.99999999999997)
    curve[4].tag = 1

    curve[5].c[0] = (33.072500000000005, 39.7375)
    curve[5].c[1] = (34.243620331950204, 36.4969398340249)
    curve[5].c[2] =  (35.15248962655602, 34.04875518672199)
    curve[5].vertex = (33.5, 38.5)
    curve[5].tag = 1

    return curve


def test_calculate_curve_area(curve1):
    assert calculate_curve_area(curve1, 0, 2) == 0.25


def test_precalculate_convexity(curve1):
    assert precalculate_convexity(curve1) == [1, 1, 1]


def test_precalculate_areas(curve1):
    assert precalculate_areas(curve1) == [0.0, 0.25, 0.5, 0.25]


def test_check_check_if_smaller_than_179(curve1):
    check_if_smaller_than_179(curve1, 1, 0) is True


def test_check_check_if_same_convexity(curve1):
    precalulcated = precalculate_convexity(curve1)
    check_if_same_convexity(curve1, 1, precalulcated, 1, 0) is True


def test_check_necesarry_condtition(curve1):
    assert check_necessary_conditions(curve1, 0, 2) is False


def test_optimize_no_optimization(curve1):
    assert optimize_curve(curve1, 0.2)[0].c == curve1[1].c
    assert optimize_curve(curve1, 0.2)[1].c == curve1[2].c
    assert optimize_curve(curve1, 0.2)[2].c == curve1[0].c


def test_optimize_true_optimization(curve2):
    assert optimize_curve(curve2, 0.2)[0].c[0][0] == pytest.approx(37.427384232140064)
    assert optimize_curve(curve2, 0.2)[0].c[1][0] == pytest.approx(37.78158820978288)
    assert optimize_curve(curve2, 0.2)[0].c[2][0] == pytest.approx(37.99365080280233)
    assert optimize_curve(curve2, 0.2)[1].c[0][0] == pytest.approx(38.6439623198522)
    assert optimize_curve(curve2, 0.2)[1].c[1][0] == pytest.approx(33.88929055983703)
    assert optimize_curve(curve2, 0.2)[1].c[2][0] == pytest.approx(33.06764705882355)
    assert optimize_curve(curve2, 0.2)[2].c[0][0] == pytest.approx(31.902941176470623)
    assert optimize_curve(curve2, 0.2)[2].c[1][0] == pytest.approx(31.796092184368767)
    assert optimize_curve(curve2, 0.2)[2].c[2][0] == pytest.approx(32.55)
    assert optimize_curve(curve2, 0.2)[3].c[0][0] == pytest.approx(34.07131120059729)
    assert optimize_curve(curve2, 0.2)[3].c[1][0] == pytest.approx(36.94680334247328)
    assert optimize_curve(curve2, 0.2)[3].c[2][0] == pytest.approx(37.20653085248496)

    assert optimize_curve(curve2, 0.2)[0].c[0][1] == pytest.approx(29.286307883929975)
    assert optimize_curve(curve2, 0.2)[0].c[1][1] == pytest.approx(29.330560818800425)
    assert optimize_curve(curve2, 0.2)[0].c[2][1] == pytest.approx(29.495074429025195)
    assert optimize_curve(curve2, 0.2)[1].c[0][1] == pytest.approx(29.999572152632723)
    assert optimize_curve(curve2, 0.2)[1].c[1][1] == pytest.approx(43.99999999999998)
    assert optimize_curve(curve2, 0.2)[1].c[2][1] == pytest.approx(43.99999999999997)
    assert optimize_curve(curve2, 0.2)[2].c[0][1] == pytest.approx(43.99999999999997)
    assert optimize_curve(curve2, 0.2)[2].c[1][1] == pytest.approx(43.43236472945888)
    assert optimize_curve(curve2, 0.2)[2].c[2][1] == pytest.approx(41.249999999999986)
    assert optimize_curve(curve2, 0.2)[3].c[0][1] == pytest.approx(36.84620441932362)
    assert optimize_curve(curve2, 0.2)[3].c[1][1] == pytest.approx(29.52659832876336)
    assert optimize_curve(curve2, 0.2)[3].c[2][1] == pytest.approx(29.396734573757527)