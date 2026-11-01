"""Invite code manager — create and redeem invite codes."""
from __future__ import annotations
import secrets
import time

_codes: dict[str, dict] = {}
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def create_code(creator: str, max_uses: int = 1, expires_days: int = 7) -> dict:
    for _ in range(100):
        code = "".join(secrets.choice(_ALPHABET) for _ in range(12))
        if code not in _codes:
            break
    _codes[code] = {"code": code, "creator": creator, "max_uses": max_uses,
                     "uses": 0, "created_at": time.time(),
                     "expires_at": time.time() + expires_days * 86400,
                     "redeemed_by": []}
    return {"code": code, "max_uses": max_uses, "expires_days": expires_days}


def redeem_code(code: str, user_id: str) -> dict:
    c = _codes.get(code)
    if not c:
        return {"redeemed": False, "error": "invalid_code"}
    if time.time() > c["expires_at"]:
        return {"redeemed": False, "error": "expired"}
    if c["uses"] >= c["max_uses"]:
        return {"redeemed": False, "error": "max_uses_reached"}
    if user_id in c["redeemed_by"]:
        return {"redeemed": False, "error": "already_redeemed"}
    c["uses"] += 1
    c["redeemed_by"].append(user_id)
    return {"redeemed": True, "code": code, "remaining": c["max_uses"] - c["uses"]}


def code_stats() -> dict:
    total = len(_codes)
    active = sum(1 for c in _codes.values() if c["uses"] < c["max_uses"] and time.time() < c["expires_at"])
    total_redemptions = sum(c["uses"] for c in _codes.values())
    return {"total_codes": total, "active": active, "exhausted": total - active,
            "total_redemptions": total_redemptions}


def clear_codes() -> None:
    _codes.clear()
