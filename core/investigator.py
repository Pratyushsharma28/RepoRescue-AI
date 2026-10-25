from pathlib import Path


def investigate(project_dir: str) -> dict:
    """Inspect the controlled sample project and diagnose the bug."""
    root = Path(project_dir).resolve()
    source_file = root / "calculator.py"

    if not source_file.is_file():
        return {
            "ok": False,
            "diagnosis": "calculator.py was not found.",
            "file": None,
        }

    source = source_file.read_text(encoding="utf-8")

    if "return price + quantity" in source:
        return {
            "ok": True,
            "diagnosis": (
                "The function adds price and quantity, "
                "but the expected behavior is multiplication."
            ),
            "file": str(source_file),
        }

    return {
        "ok": False,
        "diagnosis": "The known bug was not found; no automatic fix proposed.",
        "file": str(source_file),
    }