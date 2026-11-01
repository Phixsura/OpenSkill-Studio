"""Deployment environment manager — manage deployment environments."""
from __future__ import annotations


ENVS = {
    "development": {"tier": "dev", "auto_deploy": True, "approval_required": False},
    "staging": {"tier": "non-prod", "auto_deploy": True, "approval_required": False},
    "production": {"tier": "prod", "auto_deploy": False, "approval_required": True},
}


def list_environments() -> dict:
    return {"environments": [{**v, "name": k} for k, v in ENVS.items()],
            "total": len(ENVS)}


def deploy_to_env(env: str, version: str, approved_by: str | None = None) -> dict:
    config = ENVS.get(env)
    if not config:
        return {"deployed": False, "error": "unknown_environment"}
    if config["approval_required"] and not approved_by:
        return {"deployed": False, "error": "approval_required"}
    return {"deployed": True, "environment": env, "version": version,
            "tier": config["tier"], "approved_by": approved_by or "auto"}


def env_comparison(envs: dict[str, dict]) -> dict:
    versions = {e: d.get("version", "unknown") for e, d in envs.items()}
    all_same = len(set(versions.values())) == 1
    return {"versions": versions, "in_sync": all_same,
            "environments": list(envs.keys())}
