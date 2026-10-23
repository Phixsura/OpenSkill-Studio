"""Environment switcher — manage dev/staging/production environments."""


ENVIRONMENTS = {
    "development": {"label": "Development", "icon": "🔧", "color": "blue", "protected": False},
    "staging": {"label": "Staging", "icon": "🧪", "color": "yellow", "protected": False},
    "production": {"label": "Production", "icon": "🚀", "color": "green", "protected": True},
}


def get_environments(*, app_id: str, current: str = "development") -> dict:
    envs = []
    for env_id, meta in ENVIRONMENTS.items():
        envs.append({"id": env_id, **meta, "active": env_id == current})
    return {"app_id": app_id, "environments": envs, "current": current,
            "total": len(envs)}


def switch_environment(*, app_id: str, target: str, confirm: bool = False) -> dict:
    env = ENVIRONMENTS.get(target)
    if not env:
        return {"error": f"Unknown environment: {target}"}
    if env["protected"] and not confirm:
        return {"error": "Production switch requires explicit confirmation",
                "requires_confirm": True}
    return {"app_id": app_id, "switched_to": target,
            "label": env["label"], "protected": env["protected"]}
