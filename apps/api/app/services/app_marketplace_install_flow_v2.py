"""Install flow v2 — complete install flow with guard, permissions, config, and confirmation."""


def build_install_flow(*, app: dict, org: dict, existing_installs: list[dict]) -> dict:
    # Pre-check
    already = any(i.get("app_id") == app["id"] and i.get("status") == "active" for i in existing_installs)
    if already:
        return {"can_proceed": False, "reason": "already_installed", "steps": []}
    steps = [
        {"key": "permissions", "title": "Review Permissions", "status": "pending",
         "data": {"required": app.get("required_scopes", []), "optional": app.get("optional_scopes", [])}},
    ]
    if app.get("config_fields"):
        steps.append({"key": "configure", "title": "Configure App", "status": "pending",
                       "data": {"fields": app["config_fields"]}})
    steps.append({"key": "confirm", "title": "Confirm Installation", "status": "pending"})
    return {"can_proceed": True, "steps": steps, "step_count": len(steps),
            "app_name": app["name"], "org_name": org.get("name")}


def advance_install_step(*, flow: dict, step_key: str) -> dict:
    steps = list(flow.get("steps", []))
    for s in steps:
        if s["key"] == step_key:
            s["status"] = "completed"
    current = next((s for s in steps if s["status"] == "pending"), None)
    all_done = current is None
    return {**flow, "steps": steps, "current_step": current,
            "ready_to_install": all_done}
