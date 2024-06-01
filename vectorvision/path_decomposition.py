import numpy as np
from enum import Enum
from typing import Generator


class Turnpolicy(Enum):
    BLACK = 0
    WHITE = 1
    LEFT = 2
    RIGHT = 3
    MINORITY = 4
    MAJORITY = 5


class Bitmap:
    """Represents one of the image bitmaps (color).

    This class has methods that do produce the paths from the bitmap,
    and is used as the first stage in the potrace algorithm.

    Attributes:
        bitmap (np.ndarray): array representing the bitmap.
    """

    def __init__(self, array: np.ndarray):
        if np.isin(array, [0, 1]).all():
            self.bitmap = np.invert(array.astype("bool"))
        else:
            raise ValueError("Array must be binary.")

    def __getitem__(self, point):
        return self.bitmap[point[0]][point[1]]

    @classmethod
    def from_pil_image(cls, image):
        """Bitmap class constructor.

        Args:
            image: PIL Image object

        Returns:
            The object of type Bitmap, created from PIL Image.
        """
        return cls(np.array(image))

    def _find_next_path_start(self) -> Generator[np.ndarray, None, None]:
        """Yields next vertex coords that is the begginning of the path.

        Returns:
            Starting point.
        """

        w = np.nonzero(self.bitmap)

        while w[0].size != 0:
            leftmost_point_row_map = np.where(w[1] == w[1][0])

            leftmost_point_row_all_points = np.column_stack(
                (w[0][leftmost_point_row_map], w[1][leftmost_point_row_map])
            )
            leftmost_top_point = leftmost_point_row_all_points[0]
            yield leftmost_top_point

            # path colors are inverted on a bitmap inside find_path
            w = np.nonzero(self.bitmap)

    def _get_color_at_point(self, point: tuple[int, int]) -> int:
        """Get the color at a given point.

        Args:
            point: point in the bitmap

        Returns:
            Value of the color at the specified point. Returns 0 (white) if point is out of range (by convention).
        """
        x_size, y_size = self.bitmap.shape
        if point[1] in range(x_size) and point[0] in range(y_size):
            return self.bitmap[point[1]][point[0]]
        return 0

    def _get_next_in_direction_points(
        self, x: int, y: int, step_x: int, step_y: int
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Calculates the next 2 points forward in specified direction from given point.

        Args:
            x: x coordinate of the given point
            y: y coordinate of the given point
            step_x: step size along x-axis
            step_y: step size along y-axis

        Returns:
            Calculated points.
        """
        cy = y + (step_y - step_x - 1) // 2
        cx = x + (step_x + step_y - 1) // 2

        dy = y + (step_y + step_x - 1) // 2
        dx = x + (step_x - step_y - 1) // 2
        return (cx, cy), (dx, dy)

    def _xor_to_ref(self, x: int, y: int, xa: int) -> None:
        """Efficiently inverts the rectangle [x, xa] x [y, y1]"""
        if x < xa:
            self.bitmap[y, x:xa] ^= True
        elif x != xa:
            self.bitmap[y, xa:x] ^= True

    def _invert_color_inside_path(self, points_in_path: list[tuple[int, int]]) -> None:
        """Efficiently inverts the color inside given path.

        Args:
            points_in_path: list of points in path
        """
        if len(points_in_path) <= 0:
            return

        y1 = points_in_path[-1][1]
        xa = points_in_path[0][0]
        for n in points_in_path:
            x, y = n[0], n[1]
            if y != y1:
                self._xor_to_ref(x, min(y, y1), xa)
                y1 = y

    def _get_color_in_bounds(self, x_, y_):
        """Get the color at a given point.

        Args:
            point: point in the bitmap

        Returns:
            Value of the color at the specified point. Returns 0 if point is out of range. -1
            when white and 1 otherwise.
        """
        x_size, y_size = self.bitmap.shape
        if y_ in range(x_size) and x_ in range(y_size):
            return 1 if self.bitmap[y_][x_] else -1
        return 0

    def _get_majority_value(self, x: int, y: int) -> int:
        """Computes the "majority" value of bitmap bm at intersection (x,y). We
        assume that the bitmap is balanced at "radius" 1.

        Args:
            x: x-coord of a point
            y: y-coord of a point

        Returns:
            Majority color value.
        """
        for i in range(2, 5):
            ct = 0
            for a in range(-i + 1, i - 2):
                ct += self._get_color_in_bounds(x + a, y + i - 1)
                ct += self._get_color_in_bounds(x + i - 1, y + a)
                ct += self._get_color_in_bounds(x + a - 1, y - i)
                ct += self._get_color_in_bounds(x - i, y + a)

            if ct > 0:
                return 1
            elif ct < 0:
                return 0
        return 0

    def _find_path(
        self,
        x_start: int,
        y_start: int,
        turdsize: int,
        turnpolicy: Turnpolicy = Turnpolicy.RIGHT,
    ):
        """Compute a path in the given pixmap, separating black from white.
            Start path at the point (x_start, y_start), which must be an upper left corner
            of the path. Also compute the area enclosed by the path. Return a
            new path_t object, or NULL on error (note that a legitimate path
            cannot have length 0). Sign is required for correct interpretation
            of turnpolicies.

        Args:
            x_start: x coord of the starting point
            y_start: y coord of the starting point
            turdsize: minimal size of the path that will be produced
        """
        x = x_start
        y = y_start
        step_x = 0
        step_y = -1
        points_in_path = []
        area = 0

        while True:
            points_in_path.append((x, y))

            x += step_x
            y += step_y
            area += x * step_y

            if x == x_start and y == y_start:
                break  # end the loop if path is completed

            left, right = self._get_next_in_direction_points(x, y, step_x, step_y)

            left_color = self._get_color_at_point(left)
            right_color = self._get_color_at_point(right)

            if left_color and not right_color:
                if (
                    turnpolicy == Turnpolicy.RIGHT
                    or (
                        turnpolicy == Turnpolicy.MAJORITY
                        and self._get_majority_value(x, y)
                    )
                    or (
                        turnpolicy == Turnpolicy.MINORITY
                        and not self._get_majority_value(x, y)
                    )
                ):
                    step_x, step_y = step_y, -step_x  # right turn

                else:
                    step_x, step_y = -step_y, step_x  # left turn

            elif left_color:  # left turn
                step_x, step_y = step_y, -step_x

            elif not right_color:  # right turn
                step_x, step_y = -step_y, step_x

        self._invert_color_inside_path(points_in_path)

        if area > turdsize:
            yield points_in_path

    def generate_paths_list(
        self, turdsize: int = 2, turnpolicy=Turnpolicy.RIGHT
    ) -> list[list[tuple[int, int]]]:
        """Generate a list of paths from the bitmap.

        Args:
            turdsize: minimal area of the paths that will be produced
            turnpolicy: the turnpolicy enum value

        Returns:
            List of paths.
        """
        paths_list = list()
        for start_point in self._find_next_path_start():
            for path in self._find_path(
                start_point[1], start_point[0] + 1, turdsize, turnpolicy
            ):
                paths_list.append(path)

        return paths_list
