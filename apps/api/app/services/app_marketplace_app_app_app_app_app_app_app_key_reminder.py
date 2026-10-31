"""API key rotation reminder — alert developers about expiring keys."""
from __future__ import annotations


def check_key_expiry(keys: list[dict], *, warn_days: int = 14) -> dict:
    expiring = []
    expired = []
    ok = []
    for k in keys:
        days_left = k.get("days_until_expiry", 365)
        if days_left <= 0:
            expired.append({**k, "status": "expired"})
        elif days_left <= warn_days:
            expiring.append({**k, "status": "expiring", "urgency": "high" if days_left <= 3 else "medium"})
        else:
            ok.append({**k, "status": "ok"})
    return {"expired": expired, "expiring": expiring, "ok": ok,
            "expired_count": len(expired), "expiring_count": len(expiring),
            "needs_action": len(expired) + len(expiring) > 0}


def build_reminder_message(check_result: dict) -> str:
    if not check_result["needs_action"]:
        return "All API keys are current ✅"
    parts = []
    if check_result["expired_count"]:
        parts.append(f"❌ {check_result['expired_count']} expired")
    if check_result["expiring_count"]:
        parts.append(f"⚠️ {check_result['expiring_count']} expiring soon")
    return " · ".join(parts) + " — rotate now!"
