from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    "README.md",
    "intro.md",
    "setup.md",
    "myst.yml",
    "requirements.txt",
    "notebooks/python/python-exercises.ipynb",
    "notebooks/PyomoFundamentals/Fundamentals.ipynb",
    "notebooks/PyomoNonlinear/PyomoNonlinear.ipynb",
)
URL_RE = re.compile(r"https?://[^\s)>\"]+")


def source_text(path: Path) -> str:
    if path.suffix == ".ipynb":
        notebook = json.loads(path.read_text(encoding="utf-8"))
        chunks = []
        for cell in notebook["cells"]:
            source = cell.get("source", "")
            chunks.append("".join(source) if isinstance(source, list) else source)
        return "\n".join(chunks)
    return path.read_text(encoding="utf-8")


def iter_links() -> list[str]:
    links: set[str] = set()
    for relative_path in SOURCE_PATHS:
        text = source_text(ROOT / relative_path)
        for match in URL_RE.findall(text):
            links.add(match.rstrip(".,;"))
    return sorted(links)


def check_link(url: str, timeout: float = 15.0) -> None:
    headers = {"User-Agent": "pyomo-summer-ws-link-check/1.0"}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if 200 <= response.status < 400:
                    return
                raise AssertionError(f"{url} returned HTTP {response.status}")
        except urllib.error.HTTPError as err:
            if method == "HEAD" and err.code in {403, 405}:
                continue
            raise AssertionError(f"{url} returned HTTP {err.code}") from err
        except urllib.error.URLError as err:
            if method == "HEAD":
                continue
            raise AssertionError(f"{url} failed: {err}") from err


def main() -> None:
    failures = []
    for url in iter_links():
        try:
            check_link(url)
            print(f"ok {url}")
        except AssertionError as err:
            failures.append(str(err))
            print(f"fail {err}", file=sys.stderr)

    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
