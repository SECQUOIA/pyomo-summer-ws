from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_legacy_redirects import LEGACY_REDIRECTS


BUILD_DIR = Path("_build/html")

REQUIRED_ROUTES = (
    "index.html",
    "setup/index.html",
    "notebooks/python-basics/python-exercises/index.html",
    "notebooks/pyomo-fundamentals/fundamentals/index.html",
    "notebooks/pyomo-nonlinear/pyomononlinear/index.html",
)

NOTEBOOK_COLAB_LINKS = {
    "notebooks/python-basics/python-exercises/index.html": (
        "https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/"
        "blob/main/notebooks/01-python-basics/python-exercises.ipynb"
    ),
    "notebooks/pyomo-fundamentals/fundamentals/index.html": (
        "https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/"
        "blob/main/notebooks/02-pyomo-fundamentals/Fundamentals.ipynb"
    ),
    "notebooks/pyomo-nonlinear/pyomononlinear/index.html": (
        "https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/"
        "blob/main/notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb"
    ),
}
EXPECTED_LOGO_TEXT = "Pyomo Tutorial"


def read_site_file(relative_path: str) -> str:
    path = BUILD_DIR / relative_path
    if not path.is_file():
        raise AssertionError(f"Missing generated site file: {path}")
    return path.read_text(encoding="utf-8")


def check_required_routes() -> None:
    for route in REQUIRED_ROUTES:
        read_site_file(route)


def check_legacy_redirects() -> None:
    for legacy_path, target in LEGACY_REDIRECTS.items():
        html = read_site_file(legacy_path)
        if f'content="0; url={target}"' not in html:
            raise AssertionError(f"{legacy_path} is missing meta refresh to {target}")
        if f'window.location.replace("{target}")' not in html:
            raise AssertionError(f"{legacy_path} is missing JavaScript redirect to {target}")


def check_edit_links_hidden() -> None:
    for route in REQUIRED_ROUTES:
        html = read_site_file(route)
        if "Edit This Page" in html or "myst-fm-edit-link" in html:
            raise AssertionError(f"{route} still renders a MyST edit-page link")


def check_colab_links() -> None:
    index_html = read_site_file("index.html")
    if "Open in Colab" in index_html:
        raise AssertionError("The landing page still renders a global Colab action")

    for route, colab_url in NOTEBOOK_COLAB_LINKS.items():
        html = read_site_file(route)
        if colab_url not in html:
            raise AssertionError(f"{route} is missing direct Colab link {colab_url}")


def check_site_branding() -> None:
    html = read_site_file("index.html")
    home_link_start = html.find('class="myst-home-link')
    if home_link_start == -1:
        raise AssertionError("The generated site is missing the MyST home link")
    home_link_end = html.find("</a>", home_link_start)
    if home_link_end == -1:
        raise AssertionError("The generated site home link is malformed")
    home_link = html[home_link_start:home_link_end]

    if "Made with MyST" in home_link:
        raise AssertionError("The generated site still uses the default MyST home-link text")
    if f">{EXPECTED_LOGO_TEXT}</span>" not in home_link:
        raise AssertionError(f"The generated site home link does not show {EXPECTED_LOGO_TEXT!r}")


def main() -> None:
    check_required_routes()
    check_legacy_redirects()
    check_edit_links_hidden()
    check_colab_links()
    check_site_branding()


if __name__ == "__main__":
    main()
