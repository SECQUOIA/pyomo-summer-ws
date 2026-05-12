# Pyomo Tutorial

This repository contains the source notebooks for the [Pyomo Tutorial](https://github.com/SECQUOIA/pyomo-summer-ws). The deployed site is available at <https://secquoia.github.io/pyomo-summer-ws/>.

The [SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA) maintains the tutorial. The notebooks adapt material from the Pyomo Summer Workshop 2018 and the current [Pyomo tutorials repository](https://github.com/Pyomo/pyomo-tutorials), updating it for current Python and Pyomo workflows.

## Local build

This repository uses [uv](https://docs.astral.sh/uv/) to manage the documentation environment.

```bash
uv sync --locked --group docs
uv run --group docs python -m unittest discover -s tests
uv run --group docs jupyter book build --html --ci
uv run --group docs python tools/write_legacy_redirects.py
uv run --group docs python tools/check_static_site.py
```

To preview the built site locally:

```bash
uv run --group docs python -m http.server --directory _build/html 8000
```

The notebooks rely on Pyomo. Some examples require GLPK or IPOPT when run interactively; the Dynamic Systems simulation exercise also uses SciPy when available. The documentation build renders notebooks without executing them. See `setup.md` for Colab links and solver setup notes.

Adapted third-party tutorial material is covered in `THIRD_PARTY_NOTICES.md`.

CI installs Node for the MyST/Jupyter Book HTML build. Local contributors usually only need `uv` unless they are debugging the underlying JavaScript theme tooling. `requirements.txt` is kept as a compatibility pointer to `pyproject.toml` and `uv.lock`.

## Adding content

Add new tutorial pages or notebooks to `myst.yml` under `project.toc`. The repository keeps `_config.yml` for compatibility with older Jupyter Book tooling and shared metadata, but the deployed MyST/Jupyter Book v2 site is driven by `myst.yml`.

Legacy `.html` redirects are written after the build by `tools/write_legacy_redirects.py`. Update that mapping whenever a published route changes. The static-site checker verifies the generated routes, legacy redirects, direct Colab links, and absence of MyST edit links.

## Deployment

GitHub Actions runs the content tests, builds the MyST/Jupyter Book site, writes legacy redirects, checks generated URLs, runs static-site checks, and deploys `_build/html` to GitHub Pages on pushes to `main`. Pull requests run the same build and validation steps without deploying. A scheduled link check validates external links from the source content.
