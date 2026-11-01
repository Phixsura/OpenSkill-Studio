"""Developer workspace — manage multi-app workspace with shared resources."""


def create_workspace(*, name: str, owner_id: str, apps: list[str]) -> dict:
    if len(name) < 3:
        return {"error": "Workspace name too short"}
    return {"name": name, "owner_id": owner_id, "apps": apps, "app_count": len(apps),
            "shared_secrets": [], "shared_configs": {}, "members": [owner_id], "error": None}


def add_app_to_workspace(*, workspace: dict, app_id: str) -> dict:
    if app_id in workspace.get("apps", []):
        return {**workspace, "error": "App already in workspace"}
    apps = list(workspace.get("apps", [])) + [app_id]
    return {**workspace, "apps": apps, "app_count": len(apps), "error": None}


def get_workspace_overview(*, workspace: dict, app_details: list[dict]) -> dict:
    total_installs = sum(a.get("install_count", 0) for a in app_details)
    published = sum(1 for a in app_details if a.get("status") == "published")
    return {
        "name": workspace["name"], "app_count": len(workspace.get("apps", [])),
        "member_count": len(workspace.get("members", [])),
        "total_installs": total_installs, "published_apps": published,
    }
