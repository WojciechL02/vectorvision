import pytest
from src.polygons import (
    calc_sums,
    calc_longest_straight_subpaths,
    penalty3,
    get_best_polygon,
    Sums,
)


@pytest.fixture
def sample_path():
    return [(0, 0), (1, 1), (2, 2), (3, 3)]


@pytest.fixture
def sample_sums():
    return [
        Sums(x=0, y=0, xy=0, x2=0, y2=0),
        Sums(x=0, y=0, xy=0, x2=0, y2=0),
        Sums(x=1, y=1, xy=1, x2=1, y2=1),
        Sums(x=3, y=3, xy=5, x2=5, y2=5),
        Sums(x=6, y=6, xy=14, x2=14, y2=14),
    ]


def test_calc_sums(sample_path, sample_sums):
    assert calc_sums(sample_path) == sample_sums
