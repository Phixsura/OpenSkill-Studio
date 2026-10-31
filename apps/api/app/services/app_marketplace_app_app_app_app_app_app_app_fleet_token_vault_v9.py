"""Fleet Token Vault v9 — track API token lifecycle and usage."""
from __future__ import annotations
def fleet_token_vault_v9(tokens: list[dict]) -> dict:
    active = [t for t in tokens if t.get("active", True)]
    expired = [t for t in tokens if t.get("expired")]
    usage = sum(t.get("calls_today", 0) for t in tokens)
    return {"total": len(tokens), "active": len(active), "expired": len(expired),
            "calls_today": usage, "healthy": len(expired) == 0}
