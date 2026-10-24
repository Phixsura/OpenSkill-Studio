"""Release calendar — plan and track release schedules."""
from __future__ import annotations


def create_release(version: str, target_date: str, features: list[str],
                    owner: str = "", status: str = "planned") -> dict:
    return {"version": version, "target_date": target_date, "features": features,
            "feature_count": len(features), "owner": owner, "status": status}


def release_timeline(releases: list[dict]) -> dict:
    planned = sum(1 for r in releases if r["status"] == "planned")
    in_progress = sum(1 for r in releases if r["status"] == "in_progress")
    released = sum(1 for r in releases if r["status"] == "released")
    total_features = sum(r["feature_count"] for r in releases)
    return {"releases": releases, "total": len(releases), "planned": planned,
            "in_progress": in_progress, "released": released,
            "total_features": total_features}
