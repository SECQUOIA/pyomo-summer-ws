from __future__ import annotations

import html
from pathlib import Path


BUILD_DIR = Path("_build/html")

LEGACY_REDIRECTS = {
    "intro.html": "./",
    "notebooks/python/python-exercises.html": "../python-basics/python-exercises/",
    "notebooks/python/python-exercises/index.html": "../../python-basics/python-exercises/",
    "notebooks/PyomoFundamentals/Fundamentals.html": "../pyomo-fundamentals/fundamentals/",
    "notebooks/pyomofundamentals/fundamentals/index.html": "../../pyomo-fundamentals/fundamentals/",
    "notebooks/PyomoNonlinear/PyomoNonlinear.html": "../pyomo-nonlinear/pyomononlinear/",
    "notebooks/pyomononlinear/pyomononlinear/index.html": "../../pyomo-nonlinear/pyomononlinear/",
}


def redirect_html(target: str) -> str:
    escaped_target = html.escape(target, quote=True)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="refresh" content="0; url={escaped_target}" />
    <link rel="canonical" href="{escaped_target}" />
    <title>Redirecting...</title>
    <script>
      window.location.replace("{escaped_target}");
    </script>
  </head>
  <body>
    <p>Redirecting to <a href="{escaped_target}">{escaped_target}</a>.</p>
  </body>
</html>
"""


def write_redirects(build_dir: Path = BUILD_DIR) -> None:
    for legacy_path, target in LEGACY_REDIRECTS.items():
        output_path = build_dir / legacy_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(redirect_html(target), encoding="utf-8")


if __name__ == "__main__":
    write_redirects()
