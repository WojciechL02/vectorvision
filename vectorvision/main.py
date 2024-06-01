import os
import argparse
from PIL import Image
from vectorvision.Converter import Converter
from vectorvision.path_decomposition import Turnpolicy


def validate_input(args):
    """
    Validates the input arguments for the vectorvision CLI tool.
    This function checks if the input file exists and if its format is supported.
    It also validates the output file format if an output path is specified.

    Args:
        args (Namespace): The arguments parsed from the command line.

    Returns:
        bool: True if all validations pass, False otherwise.
    """
    if not os.path.exists(args.input_path):
        print(f"Input path: {args.input_path} does not exist.")
        return False
    name, ext = os.path.splitext(args.input_path)
    if ext not in [".jpg", ".jpeg", ".bmp", ".png", ".pbm"]:
        print(f"File format: {ext} not supported.")
        return False
    if args.output_path:
        name, ext = os.path.splitext(args.output_path)
        if ext != ".svg":
            print("Only SVG output format is supported.")
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="vectorvision - CLI tool for raster graphics vectorizing"
    )

    turnpolicy_mapping = {
        "black": Turnpolicy.BLACK,
        "white": Turnpolicy.WHITE,
        "left": Turnpolicy.LEFT,
        "right": Turnpolicy.RIGHT,
        "majority": Turnpolicy.MAJORITY,
        "minority": Turnpolicy.MINORITY,
    }

    parser.add_argument("-i", "--input-path", type=str, required=True)
    parser.add_argument("-o", "--output-path", type=str, required=False)
    parser.add_argument(
        "--turnpolicy",
        type=str,
        required=False,
        default="black",
        choices=["black", "white", "left", "right", "majority", "minority"],
        help="policy which turn take if more than one possibility is legal",
    )
    parser.add_argument(
        "--turdsize",
        type=int,
        required=False,
        default=2,
        help="drop all paths smaller than selected turdsize",
    )
    parser.add_argument(
        "--alpha-max",
        type=float,
        required=False,
        default=1.0,
        help="minimum value of alpha parameter to interpret curve as a corner",
    )
    parser.add_argument(
        "--longcurve",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="disable optimization step",
    )
    parser.add_argument(
        "--opttolerance",
        type=float,
        required=False,
        default=0.2,
        help="""maximum deviation between original and optimized curves which allow
                        to replace original ones with optimal""",
    )
    parser.add_argument(
        "--scale",
        type=float,
        required=False,
        default=1,
        help="scale factor for resulting image",
    )

    args = parser.parse_args()

    if validate_input(args):
        name, ext = os.path.splitext(args.input_path)
        output_path = args.output_path if args.output_path else name
        image = Image.open(args.input_path)
        converter = Converter(
            image,
            turnpolicy_mapping[args.turnpolicy],
            args.turdsize,
            args.alpha_max,
            args.longcurve,
            args.opttolerance,
            args.scale,
        )
        converter.run(output_path)


if __name__ == "__main__":
    main()
