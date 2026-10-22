"""API changelog — track API changes for developer communication."""

API_CHANGELOG = [
    {"version": "2024-01-01", "date": "2024-01-01", "changes": [
        {"type": "added", "description": "Developer accounts API"},
        {"type": "added", "description": "App CRUD endpoints"},
        {"type": "added", "description": "OAuth2 authorization flow"},
        {"type": "added", "description": "Webhook delivery system"},
        {"type": "added", "description": "Sandbox execution API"},
        {"type": "added", "description": "Marketplace search and discovery"},
    ]},
]


def get_api_changelog() -> list[dict]:
    return API_CHANGELOG


def get_latest_api_version() -> str:
    return API_CHANGELOG[0]["version"] if API_CHANGELOG else "unknown"


def get_changes_since(version: str) -> list[dict]:
    changes = []
    for entry in API_CHANGELOG:
        if entry["version"] > version:
            changes.extend(entry["changes"])
    return changes
