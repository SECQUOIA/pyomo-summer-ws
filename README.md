# Pyomo Tutorial

This repository contains the source notebooks for the [Pyomo Tutorial](https://github.com/SECQUOIA/pyomo-summer-ws). The tutorial adapts material from the Pyomo Summer Workshop 2018 and updates it for current Python and Pyomo workflows.

## Local build

This repository uses [uv](https://docs.astral.sh/uv/) to manage the documentation environment.

```bash
uv sync --locked --group docs
uv run --group docs python -m unittest discover -s tests
uv run --group docs jupyter book build --html --ci
```
