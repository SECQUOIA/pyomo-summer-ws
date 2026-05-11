import importlib.util
import json
import tempfile
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


def load_legacy_redirects_module():
    module_path = ROOT / "tools/write_legacy_redirects.py"
    spec = importlib.util.spec_from_file_location("write_legacy_redirects", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BookContentTests(unittest.TestCase):
    def test_python_chapter_is_python_basics(self):
        toc = (ROOT / "myst.yml").read_text()
        notebook = notebook_source("notebooks/python/python-exercises.ipynb")

        self.assertIn("title: Python Basics", toc)
        self.assertEqual(1, toc.count("title: Python Basics"))
        self.assertEqual(1, toc.count("notebooks/python/python-exercises.ipynb"))
        self.assertIn("# Python Basics", notebook)
        self.assertNotIn("# Python Fundamentals", notebook)
        self.assertNotIn("Pyomo Summer Workshop 2018 Exercise Problem - Python", toc)
        self.assertNotIn("Pyomo Summer Workshop 2018 Exercise Problem - Python", notebook)

    def test_placeholder_index_is_not_in_book(self):
        toc = (ROOT / "myst.yml").read_text()

        self.assertNotIn("genindex.md", toc)
        self.assertFalse((ROOT / "genindex.md").exists())

    def test_published_notebooks_do_not_render_todo_markers(self):
        for notebook_path in PUBLISHED_NOTEBOOKS:
            with self.subTest(notebook=notebook_path):
                self.assertNotIn("TODO", notebook_source(notebook_path))

    def test_exercise_todos_are_limited_to_learner_templates(self):
        exercise_files = tuple((ROOT / "notebooks/exercises").glob("**/*.py"))
        self.assertGreater(len(exercise_files), 0)

        for path in exercise_files:
            source = path.read_text()
            if "TODO" not in source:
                continue

            relative_path = path.relative_to(ROOT).as_posix()
            with self.subTest(path=relative_path):
                self.assertTrue(
                    path.name.endswith("_incomplete.py"),
                    f"{relative_path} contains TODO markers but is not a learner template",
                )

    def test_contact_and_branding_are_current(self):
        intro = (ROOT / "intro.md").read_text()
        config = (ROOT / "_config.yml").read_text()
        myst = (ROOT / "myst.yml").read_text()
        rendered_text = "\n".join(notebook_source(path) for path in PUBLISHED_NOTEBOOKS)
        secquoia_link = "[SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA)"

        self.assertIn("author: SECQUOIA Research Group", config)
        self.assertIn("url: https://engineering.purdue.edu/SECQUOIA", myst)
        self.assertIn(secquoia_link, intro)
        self.assertIn(secquoia_link, rendered_text)
        self.assertIn("Individual contributors include David Bernal", intro)
        self.assertNotIn("Contributors include", rendered_text)
        self.assertNotIn("David Bernal", rendered_text)
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
        self.assertIn("build-book:", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("deploy-book:", workflow)
        self.assertIn("needs: build-book", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("astral-sh/setup-uv@v6", workflow)
        self.assertIn("actions/setup-node@v4", workflow)
        self.assertIn('node-version: "20"', workflow)
        self.assertIn("uv sync --locked --group docs", workflow)
        self.assertIn("uv run --group docs python -m unittest discover -s tests", workflow)
        self.assertIn("uv run --group docs jupyter book build --html --ci", workflow)
        self.assertIn("uv run --group docs python tools/write_legacy_redirects.py", workflow)
        self.assertIn("BASE_URL: /pyomo-summer-ws", workflow)
        self.assertNotIn("BASE_URL: /pyomo-summer-ws/", workflow)
        self.assertIn('"/pyomo-summer-ws//" _build/html', workflow)
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
        self.assertIn("uv run --group docs python tools/write_legacy_redirects.py", readme)

    def test_legacy_redirect_pages_are_generated(self):
        redirects = load_legacy_redirects_module()
        expected_redirects = {
            "intro.html": "./",
            "notebooks/python/python-exercises.html": "python-exercises/",
            "notebooks/PyomoFundamentals/Fundamentals.html": "../pyomofundamentals/fundamentals/",
            "notebooks/PyomoNonlinear/PyomoNonlinear.html": "../pyomononlinear/pyomononlinear/",
        }

        self.assertEqual(expected_redirects, redirects.LEGACY_REDIRECTS)

        with tempfile.TemporaryDirectory() as tmpdir:
            build_dir = Path(tmpdir)
            redirects.write_redirects(build_dir)

            for legacy_path, target in expected_redirects.items():
                with self.subTest(legacy_path=legacy_path):
                    html = (build_dir / legacy_path).read_text()
                    self.assertIn(f'content="0; url={target}"', html)
                    self.assertIn(f'href="{target}"', html)
                    self.assertIn(f'window.location.replace("{target}")', html)

    def test_reviewed_content_polish_is_applied(self):
        python_basics = notebook_source("notebooks/python/python-exercises.ipynb")
        fundamentals = notebook_source("notebooks/PyomoFundamentals/Fundamentals.ipynb")
        nonlinear = notebook_source("notebooks/PyomoNonlinear/PyomoNonlinear.ipynb")

        self.assertNotIn("returneed", python_basics)
        self.assertNotIn("Using the list comprehensions", python_basics)
        self.assertIn(r"x_i - \sum_{j=0}^N j q_{i,j} = 0", fundamentals)
        self.assertNotIn("Woodrff", fundamentals)
        self.assertNotIn("Hagen et al. (2001)", fundamentals)
        self.assertNotIn("You should get list of errors", nonlinear)

    def test_build_artifacts_and_local_environments_are_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text().splitlines()
        config = (ROOT / "_config.yml").read_text()

        self.assertIn("_build/", gitignore)
        self.assertIn('"_build"', config)
        self.assertIn('".venv"', config)

    def test_v2_book_config_follows_quip_colab_format(self):
        myst = (ROOT / "myst.yml").read_text()
        config = (ROOT / "_config.yml").read_text()
        colab = (ROOT / "colab.html").read_text()

        self.assertIn("github: SECQUOIA/pyomo-summer-ws", myst)
        self.assertLess(myst.index("title: Open in Colab"), myst.index("title: Open an Issue"))
        self.assertIn("url: colab.html", myst)
        self.assertIn("static: true", myst)
        self.assertIn("https://github.com/SECQUOIA/pyomo-summer-ws/issues/new", myst)
        self.assertIn("url: https://github.com/SECQUOIA/pyomo-summer-ws", config)
        self.assertIn("path_to_book: .", config)
        self.assertIn("use_edit_page_button: false", config)
        self.assertIn("Built with <a href=\"https://jupyterbook.org/\">Jupyter Book</a>.", config)
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
