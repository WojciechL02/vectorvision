# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "vectorvision"
copyright = "2024, Wojciech Łapacz, Karol Ziarek, Kajetan Rożej"
author = "Wojciech Łapacz, Karol Ziarek, Kajetan Rożej"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
import pathlib
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
sys.path.insert(0, pathlib.Path(__file__).parents[2].joinpath('vectorvision').resolve().as_posix())
sys.path.insert(0, pathlib.Path(__file__).parents[2].joinpath('tests').resolve().as_posix())


extensions = [
    "sphinx.ext.autodoc",
    'sphinx.ext.autosummary',
    'sphinx_rtd_theme',
    'sphinx.ext.napoleon',
]

templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

master_doc = 'index'

source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}

# Create _static directory if it doesn't exist
if not os.path.exists(os.path.join(os.path.dirname(__file__), '_static')):
    os.makedirs(os.path.join(os.path.dirname(__file__), '_static'))

# Print sys.path to debug
print("sys.path:")
for p in sys.path:
    print(p)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
