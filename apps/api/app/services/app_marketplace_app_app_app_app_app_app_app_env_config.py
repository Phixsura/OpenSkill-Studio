"""App environment config — manage environment-specific configurations."""
from __future__ import annotations

ENVIRONMENTS = {
    "development": {"label": "Development", "icon": "🔧", "protected": False, "auto_deploy": True},
    "staging": {"label": "Staging", "icon": "🧪", "protected": False, "auto_deploy": True},
    "production": {"label": "Production", "icon": "🚀", "protected": True, "auto_deploy": False},
}


def get_env_config(env_id: str) -> dict:
    env = ENVIRONMENTS.get(env_id)
    if not env:
        return {"error": f"Unknown environment: {env_id}"}
    return {"id": env_id, **env}


def build_env_comparison() -> list[dict]:
    return [{"id": k, **v} for k, v in ENVIRONMENTS.items()]


def validate_deploy_target(env_id: str, *, has_approval: bool = False) -> dict:
    env = ENVIRONMENTS.get(env_id)
    if not env:
        return {"allowed": False, "reason": "unknown_env"}
    if env["protected"] and not has_approval:
        return {"allowed": False, "reason": "approval_required",
                "message": f"{env['label']} requires approval before deploy"}
    return {"allowed": True, "environment": env_id, "label": env["label"]}
