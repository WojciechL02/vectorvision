from src.smoothing import interval, calculate_alpha, smooth
from src.vertex_adjustment import _Curve
import pytest


def test_interval1():
    assert interval(0.5, (-12, 3), (-3, -2)) == (-7.5,  0.5)


def test_interval2():
    assert interval(0.25, (-12, 3), (-3, -2)) == (-9.75,  1.75)


def test_calculate_alpha1():
    assert calculate_alpha((-9.5, 2), (-6, 3), (-3.5, 0.5)) == pytest.approx(0.44444, abs=1e-5)


def test_calculate_alpha2():
    assert calculate_alpha((-7.94, -5.71), (-9, 4), (3.14, -3.35)) == pytest.approx(1.17055, abs=1e-5)


def test_calculate_alpha3():
    assert calculate_alpha((-6, 1), (-6, 5), (-6, 1)) == pytest.approx(1.33333, abs=1e-5)


def test_calculate_alpha4():
    assert calculate_alpha((-8.4, 6.4), (-8.6, 7.2), (-7.8, 6.8)) == 0


def test_smooth():
    curve = _Curve(5)
    curve[0].vertex = (-16, -8)
    curve[1].vertex = (-4, 12)
    curve[2].vertex = (26, 8)
    curve[3].vertex = (16, -2)
    curve[4].vertex = (3, 1.5)
    curve = smooth(curve, 1.0)
    assert curve[0].tag == 2
    assert curve[1].tag == 2
    assert curve[2].tag == 2
    assert curve[3].tag == 2
    assert curve[4].tag == 2

    assert curve[0].c[0] == (0, 0)
    assert curve[1].c[0] == (0, 0)
    assert curve[2].c[0] == (0, 0)
    assert curve[3].c[0] == (0, 0)
    assert curve[4].c[0] == (0, 0)

    assert curve[0].c[1] == (-16, -8)
    assert curve[1].c[1] == (-4, 12)
    assert curve[2].c[1] == (26, 8)
    assert curve[3].c[1] == (16, -2)
    assert curve[4].c[1] == (3, 1.5)

    assert curve[0].c[2] == (-10, 2)
    assert curve[1].c[2] == (11, 10)
    assert curve[2].c[2] == (21, 3)
    assert curve[3].c[2] == (9.5, -0.25)
    assert curve[4].c[2] == (-6.5, -3.25)

