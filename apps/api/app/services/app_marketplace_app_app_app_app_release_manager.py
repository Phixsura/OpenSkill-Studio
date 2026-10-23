"""Release manager — complete release lifecycle management."""

import html
import secrets
from datetime import datetime, timezone

RELEASE_STAGES = ["draft", "testing", "review", "approved", "published"]


def create_release(*, app_id: str, version: str, changelog: str,
                     breaking: bool = False) -> dict:
    return {
        "release_id": f"rel_{secrets.token_hex(8)}",
        "app_id": app_id, "version": version,
        "changelog": html.escape(changelog),
        "stage": "draft", "breaking": breaking,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stages": RELEASE_STAGES,
    }


def advance_stage(*, current_stage: str) -> dict:
    idx = RELEASE_STAGES.index(current_stage) if current_stage in RELEASE_STAGES else -1
    if idx >= len(RELEASE_STAGES) - 1:
        return {"error": "Already at final stage"}
    next_stage = RELEASE_STAGES[idx + 1]
    return {"previous": current_stage, "current": next_stage,
            "is_final": next_stage == "published",
            "remaining": len(RELEASE_STAGES) - idx - 2}
