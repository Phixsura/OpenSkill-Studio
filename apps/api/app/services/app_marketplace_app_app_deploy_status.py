"""Deploy status — deployment progress and environment tracking."""

import html
from datetime import datetime, timezone

ENVS = {"development": "🟢", "staging": "🟡", "production": "🔴"}


def build_deploy_status(*, deployments: list[dict]) -> dict:
    by_env: dict[str, dict] = {}
    for d in deployments:
        env = d.get("environment", "development")
        if env not in by_env or d.get("deployed_at", "") > by_env[env].get("deployed_at", ""):
            by_env[env] = {
                "environment": env,
                "icon": ENVS.get(env, "⚪"),
                "version": d.get("version", ""),
                "status": d.get("status", "unknown"),
                "deployed_at": d.get("deployed_at", ""),
                "deployer": html.escape(d.get("deployer", "")),
                "commit": d.get("commit", "")[:8],
            }
    envs = [by_env[e] for e in ["development", "staging", "production"] if e in by_env]
    versions_match = len(set(e["version"] for e in envs)) <= 1
    return {"environments": envs, "env_count": len(envs),
            "versions_in_sync": versions_match,
            "latest_deploy": max(envs, key=lambda e: e["deployed_at"]) if envs else None}
