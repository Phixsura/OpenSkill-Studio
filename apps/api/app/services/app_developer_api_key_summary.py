"""Developer API key summary — compile key usage across all apps."""

def build_key_summary(keys: list[dict]) -> dict:
    active = [k for k in keys if not k.get("revoked")]
    expired = [k for k in keys if k.get("expired")]
    total_calls = sum(k.get("total_calls", 0) for k in keys)
    return {"total": len(keys), "active": len(active), "expired": len(expired),
            "revoked": len(keys) - len(active) - len(expired), "total_api_calls": total_calls}
