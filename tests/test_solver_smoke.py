import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(relative_path):
    path = ROOT / relative_path
    subprocess.run(
        [sys.executable, path.name],
        cwd=path.parent,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )


class SolverSmokeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("glpsol"), "GLPK executable glpsol is not available")
    def test_selected_glpk_exercises_execute(self):
        scripts = (
            "notebooks/exercises/PyomoFundamentals/exercises-1/knapsack.py",
            "notebooks/exercises/PyomoFundamentals/exercises-3/lot_sizing_soln.py",
        )
        for script in scripts:
            with self.subTest(script=script):
                run_script(script)

    @unittest.skipUnless(shutil.which("ipopt"), "IPOPT executable ipopt is not available")
    def test_selected_ipopt_exercise_executes(self):
        run_script("notebooks/exercises/Nonlinear/exercises-1/rosenbrock.py")


if __name__ == "__main__":
    unittest.main()
