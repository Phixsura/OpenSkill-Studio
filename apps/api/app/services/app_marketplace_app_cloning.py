"""App cloning — create a copy of an app for forking or templating."""

from datetime import datetime, timezone


def clone_app(*, source_app: dict, new_name: str, new_slug: str, developer_id: str,
                include_config: bool = True) -> dict:
    cloned = {
        "name": new_name, "slug": new_slug, "developer_id": developer_id,
        "category": source_app.get("category"), "description": source_app.get("description"),
        "status": "draft", "cloned_from": source_app["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if include_config:
        cloned["default_config"] = source_app.get("default_config", {})
        cloned["required_scopes"] = source_app.get("required_scopes", [])
    return cloned


def validate_clone_permissions(*, source_app: dict, developer_id: str) -> dict:
    if source_app.get("allow_cloning") is False:
        return {"allowed": False, "reason": "App does not allow cloning"}
    if source_app.get("status") != "published":
        return {"allowed": False, "reason": "Can only clone published apps"}
    return {"allowed": True, "reason": None}
