# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
import mantelo
from datetime import date

parent = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "mantelo"
copyright = f"{date.today().year}, Lucy Linder"
author = "Lucy Linder"

version = mantelo.version.__version__
# The full version, including alpha/beta/rc tags.
release = mantelo.version.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.intersphinx",
    "autoapi.extension",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinx.ext.doctest",
]

autoapi_type = "python"
autoapi_dirs = ["../mantelo"]
autoapi_root = "reference"
autoapi_keep_files = False
autoapi_add_toctree_entry = False
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
]
autoapi_ignore = ["*version.py"]

intersphinx_mapping = {
    "slumber": ("https://slumber.readthedocs.io/en/stable/", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

rst_prolog = """
.. role:: python(code)
   :language: python
"""



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

html_logo = "_static/images/mantelo-text-900.png"
html_favicon = "_static/images/mantelo.ico"
html_css_files = [
    "css/custom.css",
]
html_theme_options = {
    "external_links": [
        {"name": "Github", "url": "https://github.com/derlin/mantelo"},
        {"name": "PyPi", "url": "https://pypi.org/mantelo"},
    ],
    "toc_title": "On this page",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/derlin/mantelo",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPi",
            "url": "https://pypi.org/mantelo",
            "icon": "fa-brands fa-python",
            "type": "fontawesome",
        }
    ],
}

ogp_site_url = "https://mantelo.readthedocs.io/en/latest/"
ogp_social_cards = {
    "image": "_static/images/mantelo-social-preview.png",
}
