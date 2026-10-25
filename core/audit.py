
from datetime import datetime, timezone
import json
from pathlib import Path


def build_audit_record(
    incident_id,
    status,
    approved,
    test_passed,
    failproof_trace_id=None,
):
    return {
        "incident_id": incident_id,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "approved": approved,
        "test_passed": test_passed,
        "failproof_trace_id": failproof_trace_id,
    }


def save_audit_record(record, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
