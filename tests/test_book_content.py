import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_NOTEBOOKS = (
    "notebooks/python/python-exercises.ipynb",
    "notebooks/PyomoFundamentals/Fundamentals.ipynb",
    "notebooks/PyomoNonlinear/PyomoNonlinear.ipynb",
)


def notebook_source(path):
    notebook = json.loads((ROOT / path).read_text())
    chunks = []
    for cell in notebook["cells"]:
        source = cell.get("source", "")
        chunks.append("".join(source) if isinstance(source, list) else source)
    return "\n".join(chunks)


def notebook_markdown_headings(path):
    notebook = json.loads((ROOT / path).read_text())
    headings = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", "")
        for line in ("".join(source) if isinstance(source, list) else source).splitlines():
            if line.startswith("#"):
                headings.append(line.strip())
    return headings


class BookContentTests(unittest.TestCase):
    def test_python_chapter_is_python_basics(self):
        toc = (ROOT / "myst.yml").read_text()
        notebook = notebook_source("notebooks/python/python-exercises.ipynb")

        self.assertIn("title: Python Basics", toc)
        self.assertIn("# Python Basics", notebook)
        self.assertNotIn("# Python Fundamentals", notebook)

    def test_placeholder_index_is_not_in_book(self):
        toc = (ROOT / "myst.yml").read_text()

        self.assertNotIn("genindex.md", toc)
        self.assertFalse((ROOT / "genindex.md").exists())

    def test_published_notebooks_do_not_render_todo_markers(self):
        for notebook_path in PUBLISHED_NOTEBOOKS:
            with self.subTest(notebook=notebook_path):
                self.assertNotIn("TODO", notebook_source(notebook_path))

    def test_contact_and_branding_are_current(self):
        config = (ROOT / "_config.yml").read_text()
        rendered_text = "\n".join(notebook_source(path) for path in PUBLISHED_NOTEBOOKS)

        self.assertIn("author: SECQUOIA Research Group", config)
        self.assertNotIn("dbernaln@purdue.edu", rendered_text)
        self.assertNotIn("mailto:", rendered_text)

    def test_nonlinear_solution_files_are_linked(self):
        nonlinear = notebook_source("notebooks/PyomoNonlinear/PyomoNonlinear.ipynb")

        expected_links = (
            "../exercises/Nonlinear/exercises-1/evaluation_error_bounds_soln.py",
            "../exercises/Nonlinear/exercises-1/evaluation_error_bounds2_soln.py",
            "../exercises/Nonlinear/exercises-1/formulation_1_soln.py",
            "../exercises/Nonlinear/exercises-1/formulation_4_soln.py",
            "../exercises/Nonlinear/exercises-1/reactor_design_soln.py",
        )
        for link in expected_links:
            with self.subTest(link=link):
                self.assertIn(link, nonlinear)

    def test_workflow_builds_pull_requests_without_deploying(self):
        workflow = (ROOT / ".github/workflows/tutorial.yml").read_text()

        self.assertIn("pull_request:", workflow)
        self.assertIn("astral-sh/setup-uv@v6", workflow)
        self.assertIn("actions/setup-node@v4", workflow)
        self.assertIn('node-version: "20"', workflow)
        self.assertIn("uv sync --locked --group docs", workflow)
        self.assertIn("uv run --group docs python -m unittest discover -s tests", workflow)
        self.assertIn("uv run --group docs jupyter book build --html --ci", workflow)
        self.assertNotIn("jupyter-book build .", workflow)
        self.assertNotIn("pip install -r requirements.txt", workflow)
        self.assertIn("if: github.event_name == 'push'", workflow)

    def test_docs_dependency_group_pins_jupyter_book_v2(self):
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

        docs_dependencies = pyproject["dependency-groups"]["docs"]
        self.assertIn("jupyter-book==2.1.0", docs_dependencies)
        self.assertEqual(["docs"], pyproject["tool"]["uv"]["default-groups"])
        self.assertFalse(pyproject["tool"]["uv"]["package"])

    def test_local_build_docs_match_ci_command(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("uv sync --locked --group docs", readme)
        self.assertIn("uv run --group docs python -m unittest discover -s tests", readme)
        self.assertIn("uv run --group docs jupyter book build --html --ci", readme)

    def test_build_artifacts_and_local_environments_are_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text().splitlines()
        config = (ROOT / "_config.yml").read_text()

        self.assertIn("_build/", gitignore)
        self.assertIn('"_build"', config)
        self.assertIn('".venv"', config)

    def test_v2_book_config_preserves_repository_and_colab_links(self):
        myst = (ROOT / "myst.yml").read_text()
        config = (ROOT / "_config.yml").read_text()
        colab = (ROOT / "colab.html").read_text()

        self.assertIn("github: SECQUOIA/pyomo-summer-ws", myst)
        self.assertIn("https://github.com/SECQUOIA/pyomo-summer-ws/issues/new", myst)
        self.assertIn("url: https://github.com/SECQUOIA/pyomo-summer-ws", config)
        self.assertIn("https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws", colab)
        self.assertIn("https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/blob/main/", colab)

    def test_python_pandas_import_precedes_pd_usage(self):
        notebook = json.loads((ROOT / "notebooks/python/python-exercises.ipynb").read_text())

        seen_pandas_import = False
        for cell in notebook["cells"]:
            source = "".join(cell.get("source", ""))
            if "import pandas as pd" in source:
                seen_pandas_import = True
            if "pd.read_csv" in source:
                self.assertTrue(seen_pandas_import)
                return

        self.fail("Expected the Python Basics notebook to use pd.read_csv")

    def test_python_exercises_have_subsection_headings(self):
        python_source = notebook_source("notebooks/python/python-exercises.ipynb")
        headings = notebook_markdown_headings("notebooks/python/python-exercises.ipynb")

        expected_exercise_headings = (
            *(f"### Exercise 1.{number}" for number in range(1, 8)),
            *(f"### Exercise 2.{number}" for number in range(1, 5)),
            *(f"### Exercise 3.{number}" for number in range(1, 7)),
            *(f"### Exercise 4.{number}" for number in range(1, 4)),
            *(f"### Exercise 5.{number}" for number in range(1, 3)),
        )
        for heading in expected_exercise_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, headings)

        self.assertNotIn("Inline Exercise", python_source)


if __name__ == "__main__":
    unittest.main()
