"""API version — version negotiation and deprecation management."""

import html
from datetime import datetime, timezone

VERSIONS = {
    "v1": {"status": "deprecated", "sunset_date": "2026-06-01", "released": "2024-01-01"},
    "v2": {"status": "stable", "sunset_date": None, "released": "2025-06-01"},
    "v3": {"status": "beta", "sunset_date": None, "released": "2026-09-01"},
}


def negotiate_version(*, requested: str | None = None, accept_header: str = "") -> dict:
    if requested and requested in VERSIONS:
        info = VERSIONS[requested]
        deprecated = info["status"] == "deprecated"
        return {"version": requested, "status": info["status"],
                "deprecated": deprecated,
                "sunset_date": info["sunset_date"],
                "warning": f"API {requested} is deprecated. Migrate to v2." if deprecated else None}
    # Default to latest stable
    stable = [v for v, i in VERSIONS.items() if i["status"] == "stable"]
    default = stable[-1] if stable else "v2"
    return {"version": default, "status": "stable", "deprecated": False,
            "sunset_date": None, "warning": None}


def list_versions() -> list[dict]:
    return [{"version": v, **info} for v, info in VERSIONS.items()]


def build_deprecation_notice(*, version: str, sunset_date: str,
                               migration_guide: str = "") -> dict:
    return {"version": version, "sunset_date": sunset_date,
            "migration_guide": html.escape(migration_guide),
            "days_until_sunset": max(0, (datetime.fromisoformat(sunset_date) - datetime.now(timezone.utc).replace(tzinfo=None)).days),
            "headers": {"Deprecation": "true", "Sunset": sunset_date,
                         "Link": f'</docs/migration/{version}>; rel="successor-version"'}}
