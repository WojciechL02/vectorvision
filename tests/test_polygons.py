import pytest
from vectorvision.polygons import (
    Sums,
    cyclic,
    calc_sums,
    vector_is_not_between,
    compute_direction,
    compute_vector,
    get_next_corners,
    get_pivot_points,
    get_longest_straight_subpaths,
    penalty3,
    clip_path_backward,
    clip_path_forward,
    get_segment_bounds_backward,
    get_segment_bounds_forward,
    get_best_polygon
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
def test_simple_calc_sums(sample_path, sample_sums):
    assert calc_sums(sample_path) == sample_sums
    
@pytest.fixture
def sample_cyclic_path():
    return [(123, 37), (123, 36), (124, 36), (125, 36), (126, 36), (126, 37), (126, 38), (126, 39), (125, 39), (124, 39), (123, 39), (123, 38)]

@pytest.fixture
def sample_cyclic_sums():
    return [Sums(x=0, y=0, xy=0, x2=0, y2=0), 
            Sums(x=0, y=0, xy=0, x2=0, y2=0), 
            Sums(x=0, y=-1, xy=0, x2=0, y2=1), 
            Sums(x=1, y=-2, xy=-1, x2=1, y2=2), 
            Sums(x=3, y=-3, xy=-3, x2=5, y2=3), 
            Sums(x=6, y=-4, xy=-6, x2=14, y2=4), 
            Sums(x=9, y=-4, xy=-6, x2=23, y2=4), 
            Sums(x=12, y=-3, xy=-3, x2=32, y2=5), 
            Sums(x=15, y=-1, xy=3, x2=41, y2=9), 
            Sums(x=17, y=1, xy=7, x2=45, y2=13), 
            Sums(x=18, y=3, xy=9, x2=46, y2=17), 
            Sums(x=18, y=5, xy=9, x2=46, y2=21), 
            Sums(x=18, y=6, xy=9, x2=46, y2=22)]
def test_cylic_calc_sums(sample_cyclic_path, sample_cyclic_sums):
    assert calc_sums(sample_cyclic_path) == sample_cyclic_sums

    
@pytest.mark.parametrize("a, b, c,  expected", [
    (1, 5, 10, True),
    (1, 0, 4, False),
    (1, 1, 2, True),
    (5, 5, 5, False),
    (5, 3, 5, False),
    (5, 6, 5, False),
    (10, 7, 6, False),
    (10, 0, 4, True),
])
def test_cyclic(a, b, c, expected):
    assert cyclic(a, b, c) == expected


@pytest.mark.parametrize("point1, point2, expected", [
    ((0, 0), (3, 0), 3),  # East
    ((0, 0), (0, 5), 2),  # North
    ((1, 1), (1, -1), 1),  # South
    ((5, 4), (0, 4), 0),  # West
    ((0, 0), (0, 0), 1),  # Same point  
])
def test_compute_direction(point1, point2, expected):
    assert compute_direction(point1, point2) == expected


@pytest.mark.parametrize("point1, point2, expected", [
    ((1, 1), (5, 7), [4, 6]),
    ((-1, -1), (-3, -5), [-2, -4]),
    ((1, 1), (1, 1), [0, 0]),
    ((0, 0), (0, -1), [0, -1]),
    ((5, 6), (-5, -6), [-10, -12]),
])
def test_compute_vector(point1, point2, expected):
    assert compute_vector(point1, point2) == expected


@pytest.mark.parametrize("vector, right_constraint, left_constraint, expected", [
    ([-2, -2], [1, 1], [0, 1], True),  # vector outside constraints
    ([-2, 0], [1, 1], [0, 1], True),  # vector outside constraints
    ([3, 0], [1, 1], [0, 1], True),  # vector outside constraints
    ([1, 1], [1, 0], [0, 1], False), # vector just between constraints
    ([1, 1], [1, 1], [-1, -1], False), # vector exactly on the right constraint
    ([1, 1], [-1, -1], [1, 1], False), # vector exactly on the left constraint
])
def test_vector_is_not_between(vector, right_constraint, left_constraint, expected):
    assert vector_is_not_between(vector, right_constraint, left_constraint) == expected


@pytest.mark.parametrize("path, path_len, expected", [
    # Rectangular path
    ([(123, 37), (123, 36), (124, 36), (125, 36), (126, 36), (126, 37), (126, 38), (126, 39), (125, 39), (124, 39), (123, 39), (123, 38)], 
      12, [1, 4, 4, 4, 7, 7, 7, 10, 10, 10, 0, 0]), 
    
    # Straight path
    ([(0, 0), (1, 0), (2, 0), (3, 0)], 4, [0, 0, 0, 0]), 

    # ZigZag path
     ([(0, 0), (1, 0), (1, 1), (2, 1), (2,2), (3,2), (3,3), (3,4), (2,4), (2,3), (1,3), (1,2), (0,2), (0,1)],
      14, [1, 2, 3, 4, 5, 7, 7, 8, 9, 10, 11, 12, 0, 0]),

])
def test_get_next_corners(path, path_len, expected):
    assert get_next_corners(path, path_len) == expected
    

@pytest.mark.parametrize("path, expected_pivot_points", [
    # Rectangular path
    ([(123, 37), (123, 36), (124, 36), (125, 36), (126, 36), (126, 37), (126, 38), (126, 39), (125, 39), (124, 39), (123, 39), (123, 38)],
     [5, 5, 6, 8, 8, 9, 11, 11, 0, 2, 2, 3]
     ), 
    #  Staircase path
    ([(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(1,5),(2,5),(2,6),(3,6),(3,7),(4,7),(4,6),(4,5),(4,4),(4,3),(4,2),(4,1),(4,0),(3,0),(2,0),(1,0)],
     [6, 8, 12, 12, 12, 12, 12, 12, 12, 19, 19, 19, 19, 19, 19, 19, 20, 1, 1, 1, 2, 6]
        )
])
def test_get_pivot_points(path, expected_pivot_points):
    path_len = len(path)
    next_corner = get_next_corners(path, path_len)
    pivot_points = get_pivot_points(path, next_corner, path_len)
    assert pivot_points == expected_pivot_points


@pytest.mark.parametrize("path, expected_longest_straight_subpaths", [
    # Rectangular path
    ([(123, 37), (123, 36), (124, 36), (125, 36), (126, 36), (126, 37), (126, 38), (126, 39), (125, 39), (124, 39), (123, 39), (123, 38)],
     [5, 5, 6, 8, 8, 9, 11, 11, 0, 2, 2, 3]
     ),
    # Staircase path
    ([(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(1,5),(2,5),(2,6),(3,6),(3,7),(4,7),(4,6),(4,5),(4,4),(4,3),(4,2),(4,1),(4,0),(3,0),(2,0),(1,0)],
     [6, 8, 12, 12, 12, 12, 12, 12, 12, 19, 19, 19, 19, 19, 19, 19, 20, 1, 1, 1, 2, 6]
     )
    
])
def test_get_longest_straight_subpaths(path, expected_longest_straight_subpaths):
    result = get_longest_straight_subpaths(path)
    assert result == expected_longest_straight_subpaths
    

@pytest.mark.parametrize("i, j, expected_penalty", [
    (0, 1, 0.0), 
    (0, 2, 0.577350),  
    (2, 4, 0.0),  
    (1, 8, 5.11126),  
    (4, 5, 0.0)   
])
def test_penalty3(sample_cyclic_path, sample_cyclic_sums, i, j, expected_penalty):
    result = penalty3(sample_cyclic_path, sample_cyclic_sums, i, j)
    assert result == pytest.approx(expected_penalty, 1e-4)
    

@pytest.mark.parametrize("longest_straight_subpaths, path_len, expected_forward_clips", [
    # Rectangular path
    ([5, 5, 6, 8, 8, 9, 11, 11, 0, 2, 2, 3], 12,
     [2, 4, 4, 5, 7, 7, 8, 10, 10, 11, 12, 12]),
    # Staircase path
    ([6, 8, 12, 12, 12, 12, 12, 12, 12, 19, 19, 19, 19, 19, 19, 19, 20, 1, 1, 1, 2, 6], 21,
     [1, 5, 7, 11, 11, 11, 11, 11, 11, 11, 18, 18, 18, 18, 18, 18, 18, 19, 21, 21, 21]),
])
def test_clip_path_forward(longest_straight_subpaths, path_len, expected_forward_clips):
    result = clip_path_forward(longest_straight_subpaths, path_len)
    assert result == expected_forward_clips
    
    
@pytest.mark.parametrize("forward_clips, path_len, expected_backward_clips", [
    # Rectangular path
    ([2, 4, 4, 5, 7, 7, 8, 10, 10, 11, 12, 12], 12,
     [None, 0, 0, 1, 1, 3, 4, 4, 6, 7, 7, 9, 10]),
    # Staircase path
    ([1, 5, 7, 11, 11, 11, 11, 11, 11, 11, 18, 18, 18, 18, 18, 18, 18, 19, 21, 21, 21], 21,
     [None, 0, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 10, 10, 10, 10, 10, 10, 10, 17, 18, 18]),
])
def test_clip_path_backward(forward_clips, path_len, expected_backward_clips):
    result = clip_path_backward(forward_clips, path_len)
    assert result == expected_backward_clips
    

@pytest.mark.parametrize("clips, path_len, expected_segment_num, expected_segment_bounds", [
    # Rectangular path
    ([2, 4, 4, 5, 7, 7, 8, 10, 10, 11, 12, 12], 12, 5, 
     [0, 2, 4, 7, 10, 12, None, None, None, None, None, None, None]),
    # Staircase path
    ([1, 5, 7, 11, 11, 11, 11, 11, 11, 11, 18, 18, 18, 18, 18, 18, 18, 19, 21, 21, 21], 21, 5,
     [0, 1, 5, 11, 18, 21, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]),
])
def test_segment_bounds_forward(clips, path_len, expected_segment_num, expected_segment_bounds):
    segment_num, forward_segment_bounds = get_segment_bounds_forward(clips, path_len)
    assert segment_num == expected_segment_num
    assert forward_segment_bounds ==  expected_segment_bounds
    
    
@pytest.mark.parametrize("clips, path_len, segment_num, expected_segment_bounds", [
    # Rectangular path
    ([None, 0, 0, 1, 1, 3, 4, 4, 6, 7, 7, 9, 10], 12, 5, 
     [0, 1, 4, 7, 10, 12, None, None, None, None, None, None, None]
     ),
    # Staircase path
    ([None, 0, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 10, 10, 10, 10, 10, 10, 10, 17, 18, 18], 21, 5,
    [0, 1, 3, 10, 18, 21, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
     ),
])
def test_segment_bounds_backward(clips, path_len, segment_num, expected_segment_bounds):
    backward_segment_bounds = get_segment_bounds_backward(clips, segment_num, path_len)
    assert backward_segment_bounds == expected_segment_bounds
    
    
@pytest.mark.parametrize("path, expected_polygon", [
    # Rectangular path
    ([(123, 37), (123, 36), (124, 36), (125, 36), (126, 36), (126, 37), (126, 38), (126, 39), (125, 39), (124, 39), (123, 39), (123, 38)], 
      [0, 1, 4, 7, 10]), 
    
    # Straight path
    ([(0, 0), (1, 0), (2, 0), (3, 0)], 
     [0, 3]),  
    
    # Staircase path
     ([(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(1,5),(2,5),(2,6),(3,6),(3,7),(4,7),(4,6),(4,5),(4,4),(4,3),(4,2),(4,1),(4,0),(3,0),(2,0),(1,0)],
      [0, 4, 11, 18]),

])
def test_get_best_polygon(path, expected_polygon):
    polygon = get_best_polygon(path)
    assert polygon == expected_polygon