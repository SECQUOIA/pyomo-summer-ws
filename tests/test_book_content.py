import importlib.util
import json
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_NOTEBOOKS = (
    "notebooks/01-python-basics/python-exercises.ipynb",
    "notebooks/02-pyomo-fundamentals/Fundamentals.ipynb",
    "notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb",
    "notebooks/04-structured-modeling/BlocksAndTransformations.ipynb",
    "notebooks/05-dynamic-systems/DynamicSystems.ipynb",
    "notebooks/06-gdp/GDP.ipynb",
    "notebooks/07-contrib-debugging/ContribAndDebugging.ipynb",
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


def load_static_site_module():
    module_path = ROOT / "tools/check_static_site.py"
    spec = importlib.util.spec_from_file_location("check_static_site", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BookContentTests(unittest.TestCase):
    def test_python_chapter_is_python_basics(self):
        toc = (ROOT / "myst.yml").read_text()
        notebook = notebook_source("notebooks/01-python-basics/python-exercises.ipynb")

        self.assertIn("title: Python Basics", toc)
        self.assertEqual(1, toc.count("title: Python Basics"))
        self.assertEqual(1, toc.count("notebooks/01-python-basics/python-exercises.ipynb"))
        self.assertIn("# Python Basics", notebook)
        self.assertNotIn("# Python Fundamentals", notebook)
        self.assertNotIn("Pyomo Summer Workshop 2018 Exercise Problem - Python", toc)
        self.assertNotIn("Pyomo Summer Workshop 2018 Exercise Problem - Python", notebook)

    def test_published_notebooks_follow_numbered_learning_sequence(self):
        toc = (ROOT / "myst.yml").read_text()

        self.assertEqual(tuple(sorted(PUBLISHED_NOTEBOOKS)), PUBLISHED_NOTEBOOKS)

        previous_index = -1
        for notebook_path in PUBLISHED_NOTEBOOKS:
            with self.subTest(notebook=notebook_path):
                current_index = toc.index(notebook_path)
                self.assertGreater(current_index, previous_index)
                previous_index = current_index

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
        self.assertIn("edit_url: null", myst)
        self.assertIn(secquoia_link, intro)
        self.assertIn(secquoia_link, rendered_text)
        self.assertIn("Individual contributors include David Bernal", intro)
        self.assertNotIn("Contributors include", rendered_text)
        self.assertNotIn("David Bernal", rendered_text)
        self.assertNotIn("dbernaln@purdue.edu", rendered_text)
        self.assertNotIn("mailto:", rendered_text)

    def test_nonlinear_solution_files_are_linked(self):
        nonlinear = notebook_source("notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb")

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
        self.assertIn("uv run --group docs python tools/check_static_site.py", workflow)
        self.assertIn("python tools/check_external_links.py", workflow)
        self.assertIn("schedule:", workflow)
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
        self.assertIn("pint>=0.24,<1", docs_dependencies)
        self.assertEqual(["docs"], pyproject["tool"]["uv"]["default-groups"])
        self.assertFalse(pyproject["tool"]["uv"]["package"])

    def test_local_build_docs_match_ci_command(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("uv sync --locked --group docs", readme)
        self.assertIn("uv run --group docs python -m unittest discover -s tests", readme)
        self.assertIn("uv run --group docs jupyter book build --html --ci", readme)
        self.assertIn("uv run --group docs python tools/write_legacy_redirects.py", readme)
        self.assertIn("uv run --group docs python tools/check_static_site.py", readme)
        self.assertIn("setup.md", readme)

    def test_legacy_redirect_pages_are_generated(self):
        redirects = load_legacy_redirects_module()
        expected_redirects = {
            "intro.html": "./",
            "notebooks/python/python-exercises.html": "../python-basics/python-exercises/",
            "notebooks/python/python-exercises/index.html": "../../python-basics/python-exercises/",
            "notebooks/PyomoFundamentals/Fundamentals.html": "../pyomo-fundamentals/fundamentals/",
            "notebooks/pyomofundamentals/fundamentals/index.html": "../../pyomo-fundamentals/fundamentals/",
            "notebooks/PyomoNonlinear/PyomoNonlinear.html": "../pyomo-nonlinear/pyomononlinear/",
            "notebooks/pyomononlinear/pyomononlinear/index.html": "../../pyomo-nonlinear/pyomononlinear/",
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

    def test_static_site_checker_validates_generated_behavior(self):
        checker = load_static_site_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            build_dir = Path(tmpdir)
            checker.BUILD_DIR = build_dir

            for route in checker.REQUIRED_ROUTES:
                path = build_dir / route
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("<html></html>", encoding="utf-8")

            (build_dir / "index.html").write_text(
                '<html><a class="myst-home-link"><span>Pyomo Tutorial</span></a></html>',
                encoding="utf-8",
            )

            for route, colab_url in checker.NOTEBOOK_COLAB_LINKS.items():
                path = build_dir / route
                path.write_text(f"<html><a href=\"{colab_url}\">Colab</a></html>", encoding="utf-8")

            redirects = load_legacy_redirects_module()
            redirects.write_redirects(build_dir)

            checker.main()

    def test_reviewed_content_polish_is_applied(self):
        python_basics = notebook_source("notebooks/01-python-basics/python-exercises.ipynb")
        fundamentals = notebook_source("notebooks/02-pyomo-fundamentals/Fundamentals.ipynb")
        nonlinear = notebook_source("notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb")

        self.assertNotIn("returneed", python_basics)
        self.assertNotIn("Using the list comprehensions", python_basics)
        self.assertIn(r"x_i - \sum_{j=0}^N j q_{i,j} = 0", fundamentals)
        self.assertNotIn("Woodrff", fundamentals)
        self.assertNotIn("Hagen et al. (2001)", fundamentals)
        self.assertNotIn("You should get list of errors", nonlinear)

    def test_notebooks_are_executed_for_publication(self):
        for notebook_path in PUBLISHED_NOTEBOOKS:
            notebook = json.loads((ROOT / notebook_path).read_text())
            output_cells = 0
            for index, cell in enumerate(notebook["cells"]):
                if cell.get("cell_type") != "code":
                    continue
                with self.subTest(notebook=notebook_path, cell=index):
                    self.assertIsNotNone(cell.get("execution_count"))
                    self.assertFalse(
                        any(output.get("output_type") == "error" for output in cell.get("outputs", [])),
                        f"{notebook_path} cell {index} contains saved error output",
                    )
                    if cell.get("outputs"):
                        output_cells += 1

            with self.subTest(notebook=notebook_path):
                self.assertGreater(output_cells, 0)

    def test_setup_solver_and_solution_guidance_is_published(self):
        intro = (ROOT / "intro.md").read_text()
        setup = (ROOT / "setup.md").read_text()
        myst = (ROOT / "myst.yml").read_text()
        python_basics = notebook_source("notebooks/01-python-basics/python-exercises.ipynb")
        fundamentals = notebook_source("notebooks/02-pyomo-fundamentals/Fundamentals.ipynb")
        nonlinear = notebook_source("notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb")
        structured = notebook_source("notebooks/04-structured-modeling/BlocksAndTransformations.ipynb")
        dynamic = notebook_source("notebooks/05-dynamic-systems/DynamicSystems.ipynb")
        gdp = notebook_source("notebooks/06-gdp/GDP.ipynb")
        debugging = notebook_source("notebooks/07-contrib-debugging/ContribAndDebugging.ipynb")

        self.assertIn("file: setup.md", myst)
        self.assertIn("## Learning objectives", intro)
        self.assertIn("## Learning objectives", python_basics)
        self.assertIn("## Learning objectives", fundamentals)
        self.assertIn("## Learning objectives", nonlinear)
        self.assertIn("## Learning objectives", structured)
        self.assertIn("## Learning objectives", dynamic)
        self.assertIn("## Learning objectives", gdp)
        self.assertIn("## Learning objectives", debugging)
        self.assertIn("Solutions Policy", setup)
        self.assertIn("GLPK", setup)
        self.assertIn("IPOPT", setup)
        self.assertIn("SciPy", setup)
        self.assertIn("glpsol", setup)
        self.assertIn("ipopt", setup)
        self.assertIn("self-study build includes solution cells", python_basics)

    def test_citations_and_references_are_consistent(self):
        references = (ROOT / "references.bib").read_text()
        myst = (ROOT / "myst.yml").read_text()
        fundamentals = notebook_source("notebooks/02-pyomo-fundamentals/Fundamentals.ipynb")
        nonlinear = notebook_source("notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb")
        python_basics = notebook_source("notebooks/01-python-basics/python-exercises.ipynb")

        self.assertIn("bibliography: references.bib", myst)
        self.assertIn("@book{hart2017pyomo", references)
        self.assertIn("@book{bequette2003process", references)
        self.assertIn("Hackebeil", references)
        self.assertIn("[@hart2011pyomo; @bynum2021pyomo]", python_basics)
        self.assertIn("[@hart2017pyomo; @bynum2021pyomo]", fundamentals)
        self.assertIn("[@bequette2003process]", nonlinear)

    def test_global_colab_action_is_replaced_with_direct_notebook_links(self):
        myst = (ROOT / "myst.yml").read_text()
        notebook_links = {
            "notebooks/01-python-basics/python-exercises.ipynb": notebook_source(
                "notebooks/01-python-basics/python-exercises.ipynb"
            ),
            "notebooks/02-pyomo-fundamentals/Fundamentals.ipynb": notebook_source(
                "notebooks/02-pyomo-fundamentals/Fundamentals.ipynb"
            ),
            "notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb": notebook_source(
                "notebooks/03-pyomo-nonlinear/PyomoNonlinear.ipynb"
            ),
            "notebooks/04-structured-modeling/BlocksAndTransformations.ipynb": notebook_source(
                "notebooks/04-structured-modeling/BlocksAndTransformations.ipynb"
            ),
            "notebooks/05-dynamic-systems/DynamicSystems.ipynb": notebook_source(
                "notebooks/05-dynamic-systems/DynamicSystems.ipynb"
            ),
            "notebooks/06-gdp/GDP.ipynb": notebook_source("notebooks/06-gdp/GDP.ipynb"),
            "notebooks/07-contrib-debugging/ContribAndDebugging.ipynb": notebook_source(
                "notebooks/07-contrib-debugging/ContribAndDebugging.ipynb"
            ),
        }

        self.assertNotIn("title: Open in Colab", myst)
        self.assertFalse((ROOT / "colab.html").exists())
        for notebook_path, source in notebook_links.items():
            with self.subTest(notebook=notebook_path):
                self.assertIn(
                    f"https://colab.research.google.com/github/SECQUOIA/pyomo-summer-ws/blob/main/{notebook_path}",
                    source,
                )

    def test_issue_templates_cover_public_feedback_paths(self):
        template_dir = ROOT / ".github/ISSUE_TEMPLATE"
        expected_templates = {
            "content_bug.yml": "Content bug",
            "broken_link.yml": "Broken link",
            "solver_runtime_failure.yml": "Solver or runtime failure",
            "teaching_feedback.yml": "Teaching feedback",
        }

        for filename, name in expected_templates.items():
            with self.subTest(template=filename):
                template = (template_dir / filename).read_text()
                self.assertIn(f"name: {name}", template)
                self.assertIn("body:", template)

        self.assertIn("blank_issues_enabled: true", (template_dir / "config.yml").read_text())

    def test_issue_template_labels_exist_in_repository(self):
        template_dir = ROOT / ".github/ISSUE_TEMPLATE"
        known_labels = {
            "bug",
            "documentation",
            "duplicate",
            "enhancement",
            "good first issue",
            "help wanted",
            "invalid",
            "question",
            "wontfix",
        }

        for template_path in template_dir.glob("*.yml"):
            if template_path.name == "config.yml":
                continue

            labels_line = next(
                line for line in template_path.read_text().splitlines() if line.startswith("labels:")
            )
            labels = json.loads(labels_line.removeprefix("labels:").strip())

            with self.subTest(template=template_path.name):
                self.assertLessEqual(set(labels), known_labels)

    def test_stale_tracked_files_are_removed(self):
        self.assertFalse((ROOT / "python/helper.py").exists())
        self.assertFalse((ROOT / "media/P020220518619618731410.doc").exists())

    def test_build_artifacts_and_local_environments_are_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text().splitlines()
        config = (ROOT / "_config.yml").read_text()

        self.assertIn("_build/", gitignore)
        self.assertIn('"_build"', config)
        self.assertIn('".venv"', config)

    def test_v2_book_config_follows_myst_v2_site_settings(self):
        myst = (ROOT / "myst.yml").read_text()
        config = (ROOT / "_config.yml").read_text()

        self.assertIn("edit_url: null", myst)
        self.assertIn("bibliography: references.bib", myst)
        self.assertIn("logo_text: Pyomo Tutorial", myst)
        self.assertIn("https://github.com/SECQUOIA/pyomo-summer-ws/issues/new/choose", myst)
        self.assertIn("url: https://github.com/SECQUOIA/pyomo-summer-ws", config)
        self.assertIn("path_to_book: .", config)
        self.assertIn("use_edit_page_button: false", config)
        self.assertIn("Built with <a href=\"https://jupyterbook.org/\">Jupyter Book</a>.", config)

    def test_python_pandas_import_precedes_pd_usage(self):
        notebook = json.loads((ROOT / "notebooks/01-python-basics/python-exercises.ipynb").read_text())

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
        python_source = notebook_source("notebooks/01-python-basics/python-exercises.ipynb")
        headings = notebook_markdown_headings("notebooks/01-python-basics/python-exercises.ipynb")

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
