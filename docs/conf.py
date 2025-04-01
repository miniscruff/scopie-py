import sys
from pathlib import Path

sys.path.insert(0, str(Path("..", "src").resolve()))

project = "Scopie"
copyright = "2025, Ronnie Smith"
author = "Ronnie Smith"
release = "v0.2.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"

add_module_names = False
