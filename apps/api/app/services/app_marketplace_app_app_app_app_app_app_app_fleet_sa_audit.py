"""Fleet service account audit — track unused and overprivileged SAs."""
from __future__ import annotations
def fleet_sa_audit(accounts: list[dict]) -> dict:
    unused = [a for a in accounts if a.get("last_used_days", 999) > 90]
    with_secrets = [a for a in accounts if a.get("has_long_lived_token", False)]
    return {"total": len(accounts), "unused": len(unused), "with_long_tokens": len(with_secrets),
            "clean": len(unused) == 0 and len(with_secrets) == 0}
