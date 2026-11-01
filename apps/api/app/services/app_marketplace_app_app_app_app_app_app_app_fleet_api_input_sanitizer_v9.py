"""Fleet API Input Sanitizer v9 — track input sanitization enforcement."""
from __future__ import annotations
def fleet_api_input_sanitizer_v9(endpoints: list[dict]) -> dict:
    sanitized = [e for e in endpoints if e.get("sanitization_enabled")]
    xss_blocked = sum(e.get("xss_blocked", 0) for e in endpoints)
    sqli_blocked = sum(e.get("sqli_blocked", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "sanitized": len(sanitized), "xss_blocked": xss_blocked,
            "sqli_blocked": sqli_blocked, "healthy": len(sanitized) == len(endpoints)}
