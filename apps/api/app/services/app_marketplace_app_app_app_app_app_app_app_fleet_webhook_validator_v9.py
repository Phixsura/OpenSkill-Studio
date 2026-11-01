"""Fleet Webhook Validator v9 — track webhook signature validation."""
from __future__ import annotations
def fleet_webhook_validator_v9(endpoints: list[dict]) -> dict:
    validated = sum(e.get("validated", 0) for e in endpoints)
    rejected = sum(e.get("rejected", 0) for e in endpoints)
    replay_blocked = sum(e.get("replay_blocked", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "validated": validated, "rejected": rejected,
            "replay_blocked": replay_blocked, "healthy": True}
