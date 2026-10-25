
from pathlib import Path


def can_apply_patch(
    approved: bool,
    project_root: str,
    target_path: str,
):
    root = Path(project_root).resolve()
    target = Path(target_path).resolve()

    # Only allow changes inside the project.
    if target == root or root not in target.parents:
        return False, "Target is outside the project."

    # Require human approval.
    if not approved:
        return False, "Human approval required."

    return True, "Safety checks passed."
