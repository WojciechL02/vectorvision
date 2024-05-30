import pytest
import numpy as np
from PIL import Image
from src.Converter import Converter, create_svg
from unittest.mock import mock_open, patch, MagicMock


def test_create_svg():
    name = "test_svg"
    width = 800
    height = 600
    expected_header = f"""<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
                  width="{width}" height="{height}" viewBox="0 0 {width} {height}">"""
    expected_footer = "</svg>"

    with patch("src.Converter.open", mock_open()) as mocked_file:
        with create_svg(name, width, height) as file:
            file.write("content")

        mocked_file.assert_called_once_with(f"{name}.svg", "+w")
        handle = mocked_file()

        handle.write.assert_any_call(expected_header)  # check header
        handle.write.assert_any_call("content")  # check content
        handle.write.assert_any_call(expected_footer)  # check footer
