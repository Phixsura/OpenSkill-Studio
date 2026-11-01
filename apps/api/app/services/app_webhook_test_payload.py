"""Test payload generator — generate realistic test payloads for each event type."""

from datetime import UTC, datetime
import secrets

TEST_PAYLOADS = {
    "submission.completed": lambda: {"submission_id": f"sub_{secrets.token_hex(8)}", "project_id": f"proj_{secrets.token_hex(8)}", "user_id": f"user_{secrets.token_hex(8)}", "score": 85},
    "cohort.member_added": lambda: {"cohort_id": f"coh_{secrets.token_hex(8)}", "user_id": f"user_{secrets.token_hex(8)}", "role": "learner"},
    "app.installed": lambda: {"app_id": f"app_{secrets.token_hex(8)}", "org_id": f"org_{secrets.token_hex(8)}", "installed_by": f"user_{secrets.token_hex(8)}"},
    "project.published": lambda: {"project_id": f"proj_{secrets.token_hex(8)}", "visibility": "public"},
}


def generate_test_payload(event_type: str) -> dict:
    generator = TEST_PAYLOADS.get(event_type)
    if not generator:
        return {"event_type": event_type, "test": True, "timestamp": datetime.now(UTC).isoformat()}
    return {**generator(), "test": True, "timestamp": datetime.now(UTC).isoformat()}


def list_testable_events() -> list[str]:
    return sorted(TEST_PAYLOADS.keys())
