import subprocess
import sys
from pathlib import Path


def verify(project_dir: str) -> dict:
    """Run the project's tests and report the actual process result."""
    root = Path(project_dir).resolve()

    # Only run tests from the designated sample project.
    if root.name != "sample_project":
        return {
            "ok": False,
            "exit_code": None,
            "output": "Unapproved test directory.",
        }

    test_file = root / "test_calculator.py"

    if not test_file.is_file():
        return {
            "ok": False,
            "exit_code": None,
            "output": "Test file not found.",
        }

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "-q", str(test_file),
            ],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
        )

        return {
            "ok": result.returncode == 0,
            "exit_code": result.returncode,
            "output": result.stdout + result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "exit_code": None,
            "output": "Test timed out; repair remains unverified.",
        }