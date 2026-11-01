"""Install flow summary — compile the full install flow for a user."""

def build_install_flow(*, app: dict, permissions: list[str], org: dict, has_config: bool) -> dict:
    steps = ["review_permissions"]
    if has_config:
        steps.append("configure")
    steps.append("confirm_install")
    
    return {
        "app_name": app.get("name"),
        "org_name": org.get("name"),
        "permission_count": len(permissions),
        "has_config_step": has_config,
        "steps": steps,
        "step_count": len(steps),
        "estimated_time": f"{len(steps) * 30}s",
    }
