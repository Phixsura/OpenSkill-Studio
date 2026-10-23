"""App deploy page — deployment management with environment selection."""

import html
import secrets
from datetime import datetime, timezone

ENVIRONMENTS = ["development", "staging", "production"]


def build_deploy_page(*, app_name: str, versions: list[str],
                         current_deploys: dict[str, str]) -> dict:
    envs = []
    for env in ENVIRONMENTS:
        current = current_deploys.get(env)
        envs.append({
            "environment": env,
            "current_version": current,
            "deployed": current is not None,
            "icon": {"development": "🟢", "staging": "🟡", "production": "🔴"}.get(env, "⚪"),
        })
    return {"app_name": html.escape(app_name), "environments": envs,
            "available_versions": versions,
            "deployed_count": sum(1 for e in envs if e["deployed"])}


def start_deployment(*, app_id: str, version: str, environment: str) -> dict:
    if environment not in ENVIRONMENTS:
        return {"error": f"Invalid environment: {environment}"}
    return {
        "deploy_id": f"dep_{secrets.token_hex(8)}",
        "app_id": app_id, "version": version, "environment": environment,
        "status": "deploying",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
