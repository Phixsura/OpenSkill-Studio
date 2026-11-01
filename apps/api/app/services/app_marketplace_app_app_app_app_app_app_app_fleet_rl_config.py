"""Fleet rate limit config — audit rate limiting configurations."""
from __future__ import annotations
def fleet_rl_config(endpoints: list[dict]) -> dict:
    with_rl = [e for e in endpoints if e.get("has_rate_limit", False)]
    unprotected = len(endpoints) - len(with_rl)
    return {"total": len(endpoints), "protected": len(with_rl),
            "unprotected": unprotected, "fully_covered": unprotected == 0}
