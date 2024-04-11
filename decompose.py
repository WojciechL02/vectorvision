import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
import matplotlib.patches as patches


def find_next_path_start(bm):

    w = np.nonzero(bm)

    while w[0].size != 0:
        leftmost_point_row_map = np.where(w[1] == w[1][0])   
        leftmost_point_row_all_points = np.column_stack((w[0][leftmost_point_row_map], w[1][leftmost_point_row_map]))
        leftmost_top_point = leftmost_point_row_all_points[0]
        yield(leftmost_top_point)

        w = np.nonzero(bm)


def find_path(bitmap: np.array, x_start: int, y_start: int, turdsize: int):
    
    x = x_start
    y = y_start
    step_x = 0
    step_y = -1 
    points_in_path = []
    area = 0

    while True:  # /* while this path */
        # /* add point to path */
        points_in_path.append((x, y))

        # /* move to next point */
        x += step_x
        y += step_y
        area += x * step_y

        # /* path complete? */
        if x == x_start and y == y_start:
            break

        # /* determine next direction */
        cy = y + (step_y - step_x - 1) // 2
        cx = x + (step_x + step_y - 1) // 2
        try:
            c = bitmap[cy][cx]
        except IndexError:
            c = 0
        dy = y + (step_y + step_x - 1) // 2
        dx = x + (step_x - step_y - 1) // 2
        try:
            d = bitmap[dy][dx]
        except IndexError:
            d = 0

        if c and not d:  # /* ambiguous turn */

            # if (
            #     turnpolicy == POTRACE_TURNPOLICY_RIGHT
            #     or (turnpolicy == POTRACE_TURNPOLICY_BLACK and sign)
            #     or (turnpolicy == POTRACE_TURNPOLICY_WHITE and not sign)
            #     or (turnpolicy == POTRACE_TURNPOLICY_RANDOM and detrand(x, y))
            #     or (turnpolicy == POTRACE_TURNPOLICY_MAJORITY and majority(bm, x, y))
            #     or (
            #         turnpolicy == POTRACE_TURNPOLICY_MINORITY and not majority(bm, x, y)
            #     )
            # ):

            step_x, step_y = step_y, -step_x  # /* right turn */

            # else:
            #     tmp = dirx  # /* left turn */
            #     dirx = -diry
            #     diry = tmp

        elif c:  # /* right turn */
            step_x, step_y = step_y, -step_x

        elif not d:  # /* left turn */
            step_x, step_y = -step_y, step_x

    invert_color_inside_path(bitmap, points_in_path)
    draw_path(bitmap, points_in_path)

    if area > turdsize:
        yield points_in_path


def xor_to_ref(bm: np.array, x: int, y: int, xa: int) -> None:
    if x < xa:
        bm[y, x:xa] ^= True
    elif x != xa:
        bm[y, xa:x] ^= True


def invert_color_inside_path(bm, points_in_path):
    
    # if len(points_in_path) <= 0:  # /* a path of length 0 is silly, but legal */
    #     return

    # leftmost_pixel_x = points_in_path[0][0]
    
    # for point in points_in_path:
    #     x, y = point[0], point[1]
        
    #     # /* efficiently invert the rectangle [x,xa] x [y,y1] */
    #     xor_to_ref(bm, x, y, leftmost_pixel_x)\
    if len(points_in_path) <= 0:  # /* a path of length 0 is silly, but legal */
        return

    y1 = points_in_path[-1][1]
    xa = points_in_path[0][0]
    for n in points_in_path:
        x, y = n[0], n[1]
        if y != y1:
            # /* efficiently invert the rectangle [x,xa] x [y,y1] */
            xor_to_ref(bm, x, min(y, y1), xa)
            y1 = y
    

def draw_path(bitmap: np.array, path):
    verts = path
    line_to_path = len(path) -1

    codes = [
        PlotPath.MOVETO,
    ]
    codes += [PlotPath.LINETO for _ in range(line_to_path)]

    path_to_draw = PlotPath(verts, codes)
    patch = patches.PathPatch(path_to_draw, facecolor='orange', lw=2)
    fig, ax = plt.subplots()
    ax.add_patch(patch)
    plt.imshow(bitmap)
    plt.show()


def bm_to_paths_list(bitmap: np.array, turdsize: int = 2):

    paths_list = list()

    all_big_paths = list()

    for start_point in find_next_path_start(bitmap):
        print(start_point)
        for path in find_path(bitmap, start_point[1], start_point[0]+1, turdsize=turdsize):
            all_big_paths.append(path)

    return paths_list
    


