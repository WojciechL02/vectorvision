import numpy as np

def interval(proportion: float, a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:

    """
        Calculate the point which is splitting section into two parts in given proportion

        Args:
            proportion: in which proportion segment should be splitted, ratio ax/ab
            a: first point
            b: second point

        Returns:
            point splitting segment ab in given proportion
    """

    return (a[0] + proportion * (b[0] - a[0]), a[1] + proportion * (b[1] - a[1]))

