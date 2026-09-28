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

GitHub Actions installs GLPK and IPOPT, runs the content and solver smoke tests, builds the MyST/Jupyter Book site, writes legacy redirects, checks generated URLs, runs static-site checks, and deploys `_build/html` to GitHub Pages on pushes to `main`. Pull requests run the same build and validation steps without deploying. CI sets `REQUIRE_SOLVERS=1` so a missing solver fails the build instead of skipping tests. Local runs may skip solver tests when the executables are unavailable; use `REQUIRE_SOLVERS=1 uv run --group docs python -m unittest discover -s tests -v` to require them locally as well. The documentation build renders saved notebook outputs; the smoke tests execute selected exercises, not every notebook.

The separate `external-links` workflow checks third-party URLs weekly and can also be run manually from Actions. It is separate from the PR build because remote-site outages do not indicate a dependency regression.

## Dependency updates

Dependabot groups Python patch/minor updates and GitHub Actions updates weekly. Security updates have their own group. The `Dependabot auto-merge` workflow enables native GitHub auto-merge for verified Dependabot patch/minor updates (including security updates) and all GitHub Actions updates. Major Python upgrades remain for manual review.

Keep **Allow auto-merge** enabled and protect `main` with the required **build-book** status check from GitHub Actions, requiring branches to be up to date before merging. This gate covers dependency installation, content and solver tests, and site validation. The automation refuses to enable auto-merge if that required check is missing. Its privileged workflow reads Dependabot metadata without checking out or executing PR code. After successful Dependabot CI, `Publish automatic dependency merges` waits for the merge and explicitly dispatches the build and deployment on `main`: merges made with the Actions token do not trigger ordinary push workflows. If GitHub takes more than five minutes to complete an eligible merge, that publication workflow fails visibly and can be rerun after the merge.

When a dependency PR fails CI, it stays open. Inspect the failed job in the PR's Checks tab, fix the dependency incompatibility, or rerun a transient infrastructure failure. A successful rerun can then satisfy auto-merge; major upgrades still require a manual merge. To keep an eligible PR for manual handling, disable auto-merge on that PR (a later Dependabot push will reevaluate eligibility).
