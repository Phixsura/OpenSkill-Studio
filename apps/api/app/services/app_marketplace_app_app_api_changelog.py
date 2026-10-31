"""API changelog — track API version changes with migration guides."""

import html
from datetime import datetime, timezone

API_CHANGES = {
    "2026-10-01": {
        "version": "2026-10-01", "title": "October 2026",
        "changes": [
            {"type": "added", "endpoint": "POST /api/v1/apps/{id}/publish", "description": "Publish app to marketplace"},
            {"type": "changed", "endpoint": "GET /api/v1/apps", "description": "Added pagination support"},
            {"type": "deprecated", "endpoint": "GET /api/v1/apps/search", "description": "Use query params on /api/v1/apps instead"},
        ],
    },
    "2026-07-01": {
        "version": "2026-07-01", "title": "July 2026",
        "changes": [
            {"type": "added", "endpoint": "POST /api/v1/webhooks", "description": "Webhook management"},
            {"type": "removed", "endpoint": "GET /api/v0/apps", "description": "v0 API removed"},
        ],
    },
}


def list_api_versions() -> dict:
    versions = [{"version": k, "title": v["title"], "change_count": len(v["changes"])}
                for k, v in sorted(API_CHANGES.items(), reverse=True)]
    return {"versions": versions, "total": len(versions), "latest": versions[0]["version"] if versions else None}


def get_api_changelog(*, version: str) -> dict:
    changes = API_CHANGES.get(version)
    if not changes:
        return {"error": f"Unknown version: {version}"}
    items = [{"type": c["type"], "endpoint": c["endpoint"],
              "description": html.escape(c["description"])} for c in changes["changes"]]
    has_breaking = any(c["type"] in ("removed", "changed") for c in items)
    return {"version": version, "title": changes["title"], "changes": items,
            "total": len(items), "has_breaking": has_breaking}
