"""API versioning — manage multiple API versions with deprecation."""

from datetime import datetime, timedelta
import re

VERSION_RE = re.compile(r"^v\d+$")


def create_api_version(*, app_id: str, version: str, changelog: str,
                         deprecated_endpoints: list[str] | None = None) -> dict:
    if not VERSION_RE.match(version):
        return {"error": "Version must match format 'vN' (e.g. v1, v2)"}
    return {
        "app_id": app_id,
        "version": version,
        "changelog": changelog,
        "status": "active",
        "deprecated_endpoints": deprecated_endpoints or [],
        "created_at": datetime.utcnow().isoformat(),
        "sunset_date": None,
    }


def deprecate_version(*, version: str, sunset_days: int = 90) -> dict:
    sunset_date = (datetime.utcnow() + timedelta(days=sunset_days)).isoformat()
    return {
        "version": version,
        "status": "deprecated",
        "sunset_date": sunset_date,
        "sunset_days_remaining": sunset_days,
        "migration_guide_url": f"https://docs.openskill.dev/migration/{version}",
    }


def get_version_matrix(*, versions: list[dict]) -> dict:
    active = [v for v in versions if v.get("status") == "active"]
    deprecated = [v for v in versions if v.get("status") == "deprecated"]
    sunset = [v for v in versions if v.get("status") == "sunset"]
    return {
        "versions": versions,
        "active_count": len(active),
        "deprecated_count": len(deprecated),
        "sunset_count": len(sunset),
        "latest": active[0]["version"] if active else None,
    }
