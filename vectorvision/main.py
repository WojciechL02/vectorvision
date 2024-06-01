import os
import argparse
from PIL import Image
from vectorvision.Converter import Converter


def validate_input(args):
    if not os.path.exists(args.input_path):
        print(f"Input path: {args.input_path} does not exist.")
        return False
    name, ext = os.path.splitext(args.input_path)
    if ext not in [".jpg", ".jpeg", ".bmp", ".png"]:
        print(f"File format: {ext} not supported.")
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="vectorvision - CLI tool for raster graphics vectorizing"
    )

    parser.add_argument("-i", "--input-path", type=str, required=True)
    parser.add_argument("-o", "--output-path", type=str, required=False)

    args = parser.parse_args()

    if validate_input(args):
        name, ext = os.path.splitext(args.input_path)
        output_path = args.output_path if args.output_path else name
        image = Image.open(args.input_path)
        converter = Converter(image)
        converter.run(output_path)


if __name__ == "__main__":
    main()
