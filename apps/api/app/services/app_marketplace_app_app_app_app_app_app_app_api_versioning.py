"""API versioning manager — manage API version lifecycle."""
from __future__ import annotations
import time

STATUSES = {"active", "deprecated", "sunset", "beta"}


def create_version(version: str, status: str = "active", release_date: str = "") -> dict:
    if status not in STATUSES:
        return {"created": False, "error": f"invalid status, use {sorted(STATUSES)}"}
    return {"created": True, "version": version, "status": status,
            "release_date": release_date, "endpoints": 0}


def build_version_matrix(versions: list[dict]) -> dict:
    active = [v for v in versions if v.get("status") == "active"]
    deprecated = [v for v in versions if v.get("status") == "deprecated"]
    sunset = [v for v in versions if v.get("status") == "sunset"]
    latest = active[-1]["version"] if active else None
    return {"versions": versions, "total": len(versions),
            "active_count": len(active), "deprecated_count": len(deprecated),
            "sunset_count": len(sunset), "latest": latest}


def check_deprecation(version: dict, sunset_days: int = 90) -> dict:
    status = version.get("status", "active")
    if status == "deprecated":
        return {"version": version["version"], "action_needed": True,
                "message": f"Version {version['version']} is deprecated. Migrate within {sunset_days} days."}
    if status == "sunset":
        return {"version": version["version"], "action_needed": True,
                "message": f"Version {version['version']} is sunset. No longer supported."}
    return {"version": version["version"], "action_needed": False, "message": "No action needed."}
