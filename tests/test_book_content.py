import json
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


class BookContentTests(unittest.TestCase):
    def test_python_chapter_is_python_basics(self):
        toc = (ROOT / "_toc.yml").read_text()
        notebook = notebook_source("notebooks/python/python-exercises.ipynb")

        self.assertIn("title: Python Basics", toc)
        self.assertIn("# Python Basics", notebook)
        self.assertNotIn("# Python Fundamentals", notebook)

    def test_placeholder_index_is_not_in_book(self):
        toc = (ROOT / "_toc.yml").read_text()

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
        self.assertIn("jupyter-book build .", workflow)
        self.assertIn("if: github.event_name == 'push'", workflow)


if __name__ == "__main__":
    unittest.main()
