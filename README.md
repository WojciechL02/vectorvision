# Vectorvision
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/vectorvision/badge/?version=latest)](https://vectorvision.readthedocs.io/en/latest/?badge=latest)

## Overview

Vectorvision is a tool for vectorizing raster graphics, written on the basis of the potrace (https://potrace.sourceforge.net/) program. A detailed description of the algorithm can be found in the publication about potrace (https://potrace.sourceforge.net/potrace.pdf).
For now, available color formats are binary and grayscale, RGB images are firstly converted to grayscale and vectorized. You can convert images of any common format including: png, jpg, jpeg. The output format is SVG.

## Features

The program allows you to transfer images from raster formats, e.g. PNG, to the SVG vector format. The program is available from the command line.
Features:
- Support for utility formats: PNG, JPG, JPEG, BMP.
- Output format: SVG.
- Optimization of the SVG output file for functionality.
- Starting the program from the command line.

## Tech Stack

The language of this project is Python. These are main libraries that we use:
- Sphinx
- PIL
- numpy
- shapely
- pytest


## Docs
See the documentation for detailed information:
https://vectorvision.readthedocs.io/en/latest/?badge=latest

## Installation:

To install this tool run:

`pip install vectorvision`

## Usage:

    vectorvision [-h] -i INPUT_PATH [-o OUTPUT_PATH] [--turnpolicy {black,white,left,right,majority,minority}] [--turdsize TURDSIZE] [--alpha-max ALPHA_MAX]
               [--longcurve | --no-longcurve] [--opttolerance OPTTOLERANCE] [--scale SCALE]

    vectorvision - CLI tool for raster graphics vectorizing

    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT_PATH, --input-path INPUT_PATH
    -o OUTPUT_PATH, --output-path OUTPUT_PATH
    --turnpolicy {black,white,left,right,majority,minority}
                            policy which turn take if more than one possibility is legal
    --turdsize TURDSIZE   drop all paths smaller than selected turdsize
    --alpha-max ALPHA_MAX
                            minimum value of alpha parameter to interpret curve as a corner
    --longcurve, --no-longcurve
                            disable optimization step (default: False)
    --opttolerance OPTTOLERANCE
                            maximum deviation between original and optimized curves which allow to replace original ones with optimal
    --scale SCALE         scale factor for resulting image

The output image will have the same name as input and will be saved in the same directory.

## Authors

- [@Karol Ziarek](https://github.com/ziarekk)
- [@Wojciech Lapacz](https://github.com/WojciechL02)
- [@Kajan Rożej](https://github.com/Kajotello)

## License

Please check the MIT license that is listed in this repository.
