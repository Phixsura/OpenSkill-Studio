"""Connector Marketplace — browse, install, and manage third-party connectors.

Connectors bridge the OpenSkill platform with external services
(Slack, GitHub, Jira, etc). This service manages the connector lifecycle.
"""
from __future__ import annotations
from datetime import datetime, timezone


_connectors: dict[str, dict] = {}
_installations: dict[str, list[str]] = {}  # org_id -> [connector_ids]


def publish_connector(
    connector_id: str,
    name: str,
    provider: str,
    category: str,
    version: str,
    config_schema: dict | None = None,
) -> dict:
    """Publish a connector to the marketplace."""
    now = datetime.now(timezone.utc).isoformat()
    connector = {
        "connector_id": connector_id,
        "name": name,
        "provider": provider,
        "category": category,
        "version": version,
        "config_schema": config_schema or {},
        "published_at": now,
        "install_count": 0,
        "rating": 0.0,
        "reviews": 0,
        "status": "published",
    }
    _connectors[connector_id] = connector
    return connector


def install_connector(org_id: str, connector_id: str) -> dict | None:
    """Install a connector for an organization."""
    connector = _connectors.get(connector_id)
    if not connector or connector["status"] != "published":
        return None
    if org_id not in _installations:
        _installations[org_id] = []
    if connector_id not in _installations[org_id]:
        _installations[org_id].append(connector_id)
        connector["install_count"] += 1
    return {"org_id": org_id, "connector_id": connector_id, "installed": True}


def uninstall_connector(org_id: str, connector_id: str) -> bool:
    """Uninstall a connector from an organization."""
    if org_id in _installations and connector_id in _installations[org_id]:
        _installations[org_id].remove(connector_id)
        connector = _connectors.get(connector_id)
        if connector:
            connector["install_count"] = max(0, connector["install_count"] - 1)
        return True
    return False


def list_connectors(category: str | None = None) -> list[dict]:
    """List available connectors, optionally by category."""
    results = [c for c in _connectors.values() if c["status"] == "published"]
    if category:
        results = [c for c in results if c["category"] == category]
    return sorted(results, key=lambda c: c["install_count"], reverse=True)


def get_org_connectors(org_id: str) -> list[dict]:
    """Get all connectors installed for an organization."""
    ids = _installations.get(org_id, [])
    return [_connectors[cid] for cid in ids if cid in _connectors]


def rate_connector(connector_id: str, rating: float) -> dict | None:
    """Add a rating to a connector (1.0-5.0)."""
    connector = _connectors.get(connector_id)
    if not connector:
        return None
    clamped = max(1.0, min(5.0, rating))
    old_total = connector["rating"] * connector["reviews"]
    connector["reviews"] += 1
    connector["rating"] = round((old_total + clamped) / connector["reviews"], 2)
    return connector
