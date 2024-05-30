import pytest
import numpy as np
from PIL import Image
from src.path_decomposition import Bitmap

# ============= Bitmap constructor ===============


def test_bitmap_non_binary():
    with pytest.raises(ValueError):
        Bitmap(np.array([[1, 2], [2, 1]]))


def test_bitmap_valid():
    bm = Bitmap(np.array([[1, 0], [0, 1]]))
    assert np.array_equal(bm.bitmap, np.array([[0, 1], [1, 0]]))


def test_bitmap_from_pil_image():
    image = Image.new(mode="1", size=(8, 8), color=0)
    bm = Bitmap.from_pil_image(image)
    assert (bm.bitmap == np.ones((8, 8))).all()


def test_bitmap_getitem():
    bm = Bitmap(np.array([[1, 0], [1, 1]]))
    assert bm[(0, 0)] == False


# ============= _get_color_at_point =============


def test_bitmap_get_color_at_point_out_of_range_neg():
    bm = Bitmap(np.array([[1, 1], [1, 1]]))
    assert bm._get_color_at_point((-1, -1)) == 0


def test_bitmap_get_color_at_point_out_of_range_pos():
    bm = Bitmap(np.array([[1, 1], [1, 1]]))
    assert bm._get_color_at_point((2, 2)) == 0


# ============= find_next_path_start =============


@pytest.fixture
def bm_standard():
    return Bitmap(np.array([[1, 0, 1], [1, 1, 1], [1, 1, 0]]))


@pytest.fixture
def bm_empty():
    return Bitmap(np.ones((3, 3)))


@pytest.fixture
def bm_full():
    return Bitmap(np.zeros((3, 3)))


def test_find_next_path_start_empty(bm_empty):
    starts = bm_empty._find_next_path_start()
    for i, start in enumerate(starts):
        assert start is None


def test_find_next_path_start_full(bm_full):
    starts = bm_full._find_next_path_start()
    num = 0
    for start in starts:
        num += 1
        bm_full.bitmap[start[0], start[1]] = 0

    assert num == bm_full.bitmap.shape[0] * bm_full.bitmap.shape[1]


def test_find_next_path_start_standard(bm_standard):
    expected = [np.array([0, 1]), np.array([2, 2])]
    starts = bm_standard._find_next_path_start()
    for ex in expected:
        start = next(starts)
        assert np.array_equal(start, ex)
        bm_standard.bitmap[ex[0], ex[1]] = 0


# ============= find_path =============


@pytest.fixture
def bm_one_path():
    return Bitmap(np.array([[1, 1, 1], [1, 0, 0], [1, 0, 0]]))


@pytest.fixture
def bm_minimal_path():
    return Bitmap(np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]))


@pytest.fixture
def bm_pixels_by_corner():
    return Bitmap(np.array([[1, 1, 1], [1, 0, 1], [0, 1, 1]]))


def test_find_path_square(bm_one_path):
    expected = [(1, 2), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3)]
    path = next(bm_one_path._find_path(1, 2, turdsize=1))
    assert path == expected


def test_find_path_single_pixel(bm_minimal_path):
    expected = [(1, 2), (1, 1), (2, 1), (2, 2)]
    path = next(bm_minimal_path._find_path(1, 2, turdsize=0))
    assert path == expected


def test_find_path_too_small(bm_minimal_path):
    with pytest.raises(StopIteration):
        next(bm_minimal_path._find_path(1, 2, turdsize=2))


def test_find_path_corner_alignment(bm_pixels_by_corner):
    expected = [[(1, 2), (1, 1), (2, 1), (2, 2)], [(2, 1), (2, 0), (3, 0), (3, 1)]]
    path1 = next(bm_pixels_by_corner._find_path(1, 2, turdsize=0))
    path2 = next(bm_pixels_by_corner._find_path(2, 1, turdsize=0))
    assert path1 == expected[0]
    assert path2 == expected[1]


def test_find_path_pixel_in_the_corner(bm_pixels_by_corner):
    expected = [(2, 1), (2, 0), (3, 0), (3, 1)]
    path = next(bm_pixels_by_corner._find_path(2, 1, turdsize=0))
    assert path == expected


# ============= invert_color_inside_path =============


def test_invert_color_inside_path(bm_one_path):
    points = [(1, 2), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3)]
    bm_one_path._invert_color_inside_path(points)
    assert not bm_one_path.bitmap.any()


def test_invert_color_no_change(bm_one_path):
    points = []
    bm_one_path._invert_color_inside_path(points)
    assert bm_one_path.bitmap.any()


def test_invert_color_one_pixel(bm_one_path):
    points = [
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 1),
    ]
    bm_one_path._invert_color_inside_path(points)
    assert bm_one_path.bitmap[1, 1] == 0


# ============= generate paths list ===============


def test_generate_paths_list_one_path(bm_one_path):
    expected = [[(1, 2), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3)]]
    result = bm_one_path.generate_paths_list()
    assert result == expected
