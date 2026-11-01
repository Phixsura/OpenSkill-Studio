"""API deprecation manager — manage API endpoint deprecation lifecycle."""

from datetime import datetime, timezone, timedelta


def deprecate_endpoint(*, path: str, method: str, sunset_date: str,
                         replacement: str | None = None) -> dict:
    return {"path": path, "method": method.upper(), "sunset_date": sunset_date,
            "replacement": replacement, "status": "deprecated",
            "deprecated_at": datetime.now(timezone.utc).isoformat()}


def build_deprecation_headers(*, endpoint: dict) -> dict:
    headers = {"Deprecation": endpoint["deprecated_at"], "Sunset": endpoint["sunset_date"]}
    if endpoint.get("replacement"):
        headers["Link"] = f'<{endpoint["replacement"]}>; rel="successor-version"'
    return headers


def check_sunset_status(*, endpoints: list[dict]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    active = [e for e in endpoints if e.get("sunset_date", "9999") > now]
    expired = [e for e in endpoints if e.get("sunset_date", "9999") <= now]
    return {"active_deprecations": len(active), "expired": len(expired),
            "endpoints": endpoints, "needs_cleanup": len(expired) > 0}
