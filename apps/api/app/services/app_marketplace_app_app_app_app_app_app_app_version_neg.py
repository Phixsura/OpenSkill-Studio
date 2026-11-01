"""API version negotiator — negotiate API version from request headers."""
from __future__ import annotations


def negotiate_version(accept_header: str, available: list[str], default: str = "") -> dict:
    if not available:
        return {"version": "", "matched": False, "reason": "no_versions_available"}
    default = default or available[-1]
    # Parse Accept-Version or API-Version header
    requested = accept_header.strip()
    if not requested:
        return {"version": default, "matched": True, "negotiated": False}
    if requested in available:
        return {"version": requested, "matched": True, "negotiated": True}
    # Try prefix matching (e.g., "v2" matches "v2.1")
    for v in reversed(available):
        if v.startswith(requested):
            return {"version": v, "matched": True, "negotiated": True, "prefix_match": True}
    return {"version": default, "matched": False, "fallback": True,
            "requested": requested}


def supported_versions(versions: list[dict]) -> dict:
    active = [v for v in versions if v.get("status") == "active"]
    deprecated = [v for v in versions if v.get("status") == "deprecated"]
    return {"active": [v["version"] for v in active],
            "deprecated": [v["version"] for v in deprecated],
            "latest": active[-1]["version"] if active else ""}
