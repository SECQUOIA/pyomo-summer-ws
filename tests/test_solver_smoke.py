import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(relative_path):
    path = ROOT / relative_path
    result = subprocess.run(
        [sys.executable, path.name],
        cwd=path.parent,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode:
        raise AssertionError(
            f"{relative_path} exited with {result.returncode}\n"
            f"{result.stdout}\n{result.stderr}"
        )


class SolverSmokeTests(unittest.TestCase):
    def require_solver(self, executable):
        if shutil.which(executable):
            return
        message = f"Required solver executable {executable} is not available"
        if os.environ.get("REQUIRE_SOLVERS") == "1":
            self.fail(message)
        self.skipTest(message)

    def test_selected_glpk_exercises_execute(self):
        self.require_solver("glpsol")
        scripts = (
            "notebooks/exercises/PyomoFundamentals/exercises-1/knapsack.py",
            "notebooks/exercises/PyomoFundamentals/exercises-3/lot_sizing_soln.py",
        )
        for script in scripts:
            with self.subTest(script=script):
                run_script(script)

    def test_selected_ipopt_exercise_executes(self):
        self.require_solver("ipopt")
        run_script("notebooks/exercises/Nonlinear/exercises-1/rosenbrock.py")


if __name__ == "__main__":
    unittest.main()
