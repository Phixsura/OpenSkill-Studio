"""Environment switcher — manage and switch between dev/staging/production."""
from __future__ import annotations

ENVIRONMENTS = {
    "development": {"label": "Development", "icon": "🔧", "color": "blue", "url": "https://dev.openskill.io"},
    "staging": {"label": "Staging", "icon": "🧪", "color": "yellow", "url": "https://staging.openskill.io"},
    "production": {"label": "Production", "icon": "🚀", "color": "green", "url": "https://app.openskill.io"},
}


def get_environments() -> list[dict]:
    return [{"id": k, **v} for k, v in ENVIRONMENTS.items()]


def get_environment(env_id: str) -> dict:
    env = ENVIRONMENTS.get(env_id)
    if not env:
        return {"error": f"Unknown environment: {env_id}"}
    return {"id": env_id, **env}


def compare_environments(env_a: str, env_b: str) -> dict:
    a = ENVIRONMENTS.get(env_a)
    b = ENVIRONMENTS.get(env_b)
    if not a or not b:
        return {"error": "Invalid environment"}
    return {"from": {"id": env_a, **a}, "to": {"id": env_b, **b},
            "promotion": env_a in ("development", "staging") and env_b == "production"}
