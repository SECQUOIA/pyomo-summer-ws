# Setup and Solvers

This page collects the commands and solver notes needed to build the site or run the notebooks.

## Colab

Use these links to open the published notebooks directly in Google Colab:

- [Python Basics](https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/blob/main/notebooks/01-python-basics/python-exercises.ipynb)
- [Pyomo Fundamentals](https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/blob/main/notebooks/02-pyomo-fundamentals/Fundamentals.ipynb)
- [Pyomo Nonlinear Problems](https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/blob/main/notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb)

The nonlinear notebook installs the IDAES extension bundle in Colab when IPOPT is missing. The fundamentals notebook uses GLPK for mixed-integer examples; install GLPK before running those cells in a fresh runtime.

## Local Environment

The documentation environment is managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked --group docs
uv run --group docs python -m unittest discover -s tests
env BASE_URL=/pyomo-summer-ws uv run --group docs jupyter book build --html --ci
uv run --group docs python tools/write_legacy_redirects.py
uv run --group docs python tools/check_static_site.py
uv run --group docs python -m http.server --directory _build/html 8000
```

The documentation build renders notebooks without executing them. Running the notebooks locally also requires solver executables on `PATH`.

## Solver Notes

Pyomo calls external solvers through `SolverFactory`. The examples use:

- GLPK through `glpsol` for linear and mixed-integer examples.
- IPOPT through `ipopt` for nonlinear examples.

On Ubuntu, GLPK is available from the system package manager:

```bash
sudo apt-get install glpk-utils
```

For local IPOPT or cross-platform GLPK installs, a Conda environment from conda-forge is usually the most direct route:

```bash
conda install -c conda-forge glpk ipopt
```

Confirm solver discovery before running solver-dependent examples:

```bash
uv run --group docs python - <<'PY'
import shutil

for solver in ("glpsol", "ipopt"):
    print(f"{solver}: {shutil.which(solver) or 'not found'}")
PY
```

## Solutions Policy

The public site is a self-study build. It includes solution cells or solution-file links close to each exercise so learners can check their work. Instructors using these materials for a live workshop can remove the solution cells or distribute only the `_incomplete.py` exercise files.
