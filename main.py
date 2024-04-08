import cv2
import PIL
import argparse
import numpy
import sphinx
import pytest


def main():
    parser = argparse.ArgumentParser(
        description="vectorvision - CLI tool for raster graphics vectorizing"
    )

    parser.add_argument("--input-path", type=str, required=True)
    parser.add_argument("--save-path", type=str, required=True)

    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()
