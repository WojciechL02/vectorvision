import pytest
import numpy as np
from src.decompose import find_next_path_start, find_path, invert_color_inside_path

# ============= find_next_path_start =============


@pytest.fixture
def bm_standard():
    return np.array([[0, 1, 0], [0, 0, 0], [0, 0, 1]])


@pytest.fixture
def bm_empty():
    return np.zeros((3, 3))


@pytest.fixture
def bm_full():
    return np.ones((3, 3))


def test_find_next_path_start_empty(bm_empty):
    starts = find_next_path_start(bm_empty)
    for i, start in enumerate(starts):
        assert start is None


def test_find_next_path_start_full(bm_full):
    starts = find_next_path_start(bm_full)
    num = 0
    for start in starts:
        num += 1
        bm_full[start[0], start[1]] = 0

    assert num == bm_full.shape[0] * bm_full.shape[1]


def test_find_next_path_start_standard(bm_standard):
    expected = [np.array([0, 1]), np.array([2, 2])]
    starts = find_next_path_start(bm_standard)
    for ex in expected:
        start = next(starts)
        assert np.array_equal(start, ex)
        bm_standard[ex[0], ex[1]] = 0


# ============= find_path =============


@pytest.fixture
def bm_one_path():
    return np.array([[0, 0, 0], [0, 1, 1], [0, 1, 1]])


@pytest.fixture
def bm_minimal_path():
    return np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])


@pytest.fixture
def bm_pixels_by_corner():
    return np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0]])


def test_find_path_square(bm_one_path):
    expected = [(1, 2), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3)]
    path = next(find_path(bm_one_path, 1, 2, turdsize=1))
    assert path == expected


def test_find_path_single_pixel(bm_minimal_path):
    expected = [(1, 2), (1, 1), (2, 1), (2, 2)]
    path = next(find_path(bm_minimal_path, 1, 2, turdsize=0))
    assert path == expected


def test_find_path_too_small(bm_minimal_path):
    with pytest.raises(StopIteration):
        next(find_path(bm_minimal_path, 1, 2, turdsize=2))


def test_find_path_corner_alignment(bm_pixels_by_corner):
    expected = [[(1, 2), (1, 1), (2, 1), (2, 2)], [(2, 1), (2, 0), (3, 0), (3, 1)]]
    path1 = next(find_path(bm_pixels_by_corner, 1, 2, turdsize=0))
    path2 = next(find_path(bm_pixels_by_corner, 2, 1, turdsize=0))
    assert path1 == expected[0]
    assert path2 == expected[1]


def test_find_path_pixel_in_the_corner(bm_pixels_by_corner):
    expected = [(2, 1), (2, 0), (3, 0), (3, 1)]
    path = next(find_path(bm_pixels_by_corner, 2, 1, turdsize=0))
    assert path == expected


# ============= invert_color_inside_path =============


def test_invert_color_inside_path(bm_one_path):
    points = [(1, 2), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3)]
    invert_color_inside_path(bm_one_path, points)
    assert not bm_one_path.any()


def test_invert_color_no_change(bm_one_path):
    points = []
    invert_color_inside_path(bm_one_path, points)
    assert bm_one_path.any()
