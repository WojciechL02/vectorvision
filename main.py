import os
import argparse
from PIL import Image
from src.Converter import Converter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="vectorvision - CLI tool for raster graphics vectorizing"
    )

    parser.add_argument("-i", "--input-path", type=str, required=True)
    parser.add_argument("-o", "--output-path", type=str, required=False)

    args = parser.parse_args()

    name, ext = os.path.splitext(args.input_path)
    output_path = args.output_path if args.output_path else name
    image = Image.open(args.input_path)
    converter = Converter(image)
    converter.run(output_path)


if __name__ == "__main__":
    main()
