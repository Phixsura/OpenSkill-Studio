"""Update flow — check compatibility, migrate config, switch versions."""

from datetime import datetime, timezone


def check_update_compatibility(*, current_version: dict, target_version: dict) -> dict:
    breaking = target_version.get("breaking_changes", [])
    deprecated = target_version.get("deprecated_features", [])
    current_features = set(current_version.get("features", []))
    removed = [f for f in current_features if f in [d.get("feature") for d in deprecated]]
    return {
        "compatible": len(breaking) == 0,
        "breaking_changes": breaking,
        "deprecated_features": deprecated,
        "removed_features": removed,
        "requires_config_migration": target_version.get("config_schema_version") != current_version.get("config_schema_version"),
    }


def migrate_config(*, old_config: dict, migration_rules: list[dict]) -> dict:
    new_config = dict(old_config)
    applied = []
    for rule in migration_rules:
        if rule["type"] == "rename":
            if rule["from"] in new_config:
                new_config[rule["to"]] = new_config.pop(rule["from"])
                applied.append(rule)
        elif rule["type"] == "default":
            if rule["key"] not in new_config:
                new_config[rule["key"]] = rule["value"]
                applied.append(rule)
        elif rule["type"] == "remove":
            new_config.pop(rule["key"], None)
            applied.append(rule)
    return {"config": new_config, "applied_rules": len(applied)}


def execute_update(*, installation_id: str, target_version_id: str, new_config: dict) -> dict:
    return {
        "installation_id": installation_id,
        "previous_version_id": None,
        "new_version_id": target_version_id,
        "config": new_config,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "rollback_available": True,
    }
