
from pathlib import Path
from core.investigator import investigate
from core.repairer import propose_patch, apply_patch
from core.verifier import verify
from core.failproof import POLICY_STATUS, repair_trace


def _run_repair(project_dir: str, approval: bool, trace) -> dict:
    root = Path(project_dir).resolve()

    # The caller must explicitly select the sample workspace.
    if root.name != "sample_project":
        return {
            "status": "BLOCKED",
            "reason": "Only the sample project is permitted.",
        }

    diagnosis = trace.tool("repository_investigation", lambda: investigate(str(root)))

    if not diagnosis["ok"]:
        return {
            "status": "FAILED",
            "diagnosis": diagnosis,
        }

    patch = trace.tool("patch_proposal", lambda: propose_patch(str(root)))

    if not patch["ok"]:
        return {
            "status": "BLOCKED",
            "diagnosis": diagnosis,
            "patch": patch,
        }

    if not approval:
        return {
            "status": "AWAITING_APPROVAL",
            "diagnosis": diagnosis,
            "patch": {
                "file": patch["file"],
                "original": patch["original"],
                "updated": patch["updated"],
                "reason": patch["reason"],
                "project_dir": patch["project_dir"],
            },
            "application": {"ok": False, "reason": "Patch requires approval."},
            "verification": None,
        }

    result = trace.tool(
        "approved_patch_application",
        lambda: apply_patch(patch, approval=True),
        input_data={"target": patch.get("file"), "human_approved": True},
    )

    if not result["ok"]:
        return {
            "status": "FAILED",
            "diagnosis": diagnosis,
            "patch": {"file": patch["file"], "updated": patch["updated"], "reason": patch["reason"]},
            "application": result,
            "verification": None,
        }

    verification = trace.tool("pytest_verification", lambda: verify(str(root)))

    return {
        "status": "VERIFIED" if verification["ok"] else "VERIFICATION_FAILED",
        "diagnosis": diagnosis,
        "patch": {
            "reason": patch["reason"],
            "updated": patch["updated"],
        },
        "application": result,
        "verification": verification,
    }


def run_repair(project_dir: str, approval: bool = False) -> dict:
    """Run the workflow and attach its actual Failproof session identity.

    The custom-agent SDK is tracing-only. Failproof policy outcomes remain
    NOT_EVALUATED until a custom runtime enforcement hook is validated.
    """
    with repair_trace() as trace:
        result = _run_repair(project_dir, approval, trace)
    result["failproof"] = {
        "session_id": trace.session_id if trace.sdk_available else None,
        "sdk_available": trace.sdk_available,
        "policy_outcome": POLICY_STATUS,
    }
    return result
    
