"""Feature flag service — toggle features per user/org/global."""


def evaluate_flags(*, user_id: str, org_id: str | None = None,
                     flags: dict | None = None) -> dict:
    defaults = {
        "dark_mode": {"enabled": True, "rollout": 100},
        "new_editor": {"enabled": True, "rollout": 50},
        "beta_analytics": {"enabled": False, "rollout": 0},
        "ai_suggestions": {"enabled": True, "rollout": 25},
        "bulk_actions": {"enabled": True, "rollout": 100},
    }
    registry = flags or defaults
    evaluated = {}
    for key, cfg in registry.items():
        if not cfg["enabled"]:
            evaluated[key] = False
            continue
        rollout = cfg["rollout"]
        user_hash = abs(hash(f"{key}:{user_id}")) % 100
        evaluated[key] = user_hash < rollout
    return {"user_id": user_id, "org_id": org_id, "flags": evaluated,
            "total": len(evaluated), "enabled_count": sum(1 for v in evaluated.values() if v)}


def create_flag(*, name: str, description: str, rollout: int = 0) -> dict:
    if not name.replace("_", "").isalnum():
        return {"error": "Flag name must be alphanumeric with underscores"}
    return {"name": name, "description": description, "enabled": rollout > 0,
            "rollout": min(max(rollout, 0), 100), "created": True}
