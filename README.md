# Pyomo Tutorial

This repository contains the source notebooks for the [Pyomo Tutorial](https://github.com/SECQUOIA/pyomo-summer-ws). The deployed site is available at <https://secquoia.github.io/pyomo-summer-ws/>.

The [SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA) maintains the tutorial. The notebooks adapt material from the Pyomo Summer Workshop 2018 and update it for current Python and Pyomo workflows.

## Local build

This repository uses [uv](https://docs.astral.sh/uv/) to manage the documentation environment.

```bash
uv sync --locked --group docs
uv run --group docs python -m unittest discover -s tests
uv run --group docs jupyter book build --html --ci
uv run --group docs python tools/write_legacy_redirects.py
```

To preview the built site locally:

```bash
uv run --group docs python -m http.server --directory _build/html 8000
```

The notebooks rely on Pyomo. Some examples require GLPK or IPOPT when run interactively; the documentation build renders notebooks without executing them.

## Adding content

Add new tutorial pages or notebooks to `myst.yml` under `project.toc`. The repository keeps `_config.yml` for compatibility with older Jupyter Book tooling and shared metadata, but the deployed MyST/Jupyter Book v2 site is driven by `myst.yml`.

Legacy `.html` redirects are written after the build by `tools/write_legacy_redirects.py`. Update that mapping whenever a published route changes.

## Deployment

GitHub Actions runs the content tests, builds the MyST/Jupyter Book site, writes legacy redirects, checks generated URLs, and deploys `_build/html` to GitHub Pages on pushes to `main`. Pull requests run the same build and validation steps without deploying.
