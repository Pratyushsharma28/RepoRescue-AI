from pathlib import Path


def propose_patch(project_dir: str, file_name: str = "calculator.py") -> dict:
    """Propose a minimal patch for the known demonstration bug."""
    root = Path(project_dir).resolve()
    target = (root / file_name).resolve()

    # Keep all writes within the selected sample project.
    if target.parent != root or target.name != "calculator.py":
        return {"ok": False, "reason": "File is outside the permitted scope."}

    if not target.is_file():
        return {"ok": False, "reason": "Target file does not exist."}

    original = target.read_text(encoding="utf-8")
    faulty = "return price + quantity"
    corrected = "return price * quantity"

    if original.count(faulty) != 1:
        return {
            "ok": False,
            "reason": "Expected exactly one known faulty expression.",
        }

    updated = original.replace(faulty, corrected, 1)

    return {
        "ok": True,
        "file": str(target),
        "project_dir": str(root),
        "original": original,
        "updated": updated,
        "reason": "Replace addition with multiplication.",
    }


def apply_patch(patch: dict, approval: bool = False) -> dict:
    """Apply a validated patch only after explicit approval."""
    if not patch.get("ok"):
        return {"ok": False, "reason": "Patch validation failed."}

    if not approval:
        return {"ok": False, "reason": "Patch requires approval."}

    try:
        root = Path(patch["project_dir"]).resolve(strict=True)
        target = Path(patch["file"]).resolve(strict=True)
    except (KeyError, OSError, TypeError):
        return {"ok": False, "reason": "Patch target is unavailable."}

    if root.name != "sample_project" or target.parent != root or target.name != "calculator.py":
        return {"ok": False, "reason": "Unexpected target file."}

    if target.read_text(encoding="utf-8") != patch["original"]:
        return {
            "ok": False,
            "reason": "File changed after the patch was proposed.",
        }

    target.write_text(patch["updated"], encoding="utf-8")
    return {"ok": True, "reason": "Patch applied."}
