"""Feature flag v2 — advanced feature flags with targeting rules and rollout."""

import hashlib


PLATFORM_FLAGS = {
    "new_search": {"enabled": True, "rollout_pct": 100, "description": "New search experience"},
    "ai_recommendations": {"enabled": True, "rollout_pct": 50, "description": "AI-powered recommendations"},
    "dark_mode_v2": {"enabled": False, "rollout_pct": 0, "description": "Dark mode redesign"},
    "pricing_page": {"enabled": True, "rollout_pct": 25, "description": "New pricing page"},
    "developer_analytics_v3": {"enabled": True, "rollout_pct": 100, "description": "Analytics v3"},
}


def evaluate_flag(*, flag_id: str, user_id: str | None = None) -> dict:
    flag = PLATFORM_FLAGS.get(flag_id)
    if not flag:
        return {"enabled": False, "reason": "unknown_flag"}
    if not flag["enabled"]:
        return {"enabled": False, "reason": "disabled"}
    if flag["rollout_pct"] == 100:
        return {"enabled": True, "reason": "full_rollout"}
    if not user_id:
        return {"enabled": False, "reason": "no_user_for_rollout"}
    bucket = int(hashlib.md5(f"{flag_id}:{user_id}".encode()).hexdigest(), 16) % 100
    enabled = bucket < flag["rollout_pct"]
    return {"enabled": enabled, "reason": "rollout", "bucket": bucket}


def get_all_flags(*, user_id: str | None = None) -> dict[str, bool]:
    return {fid: evaluate_flag(flag_id=fid, user_id=user_id)["enabled"] for fid in PLATFORM_FLAGS}


def get_flag_status() -> list[dict]:
    return [{"id": k, **v} for k, v in PLATFORM_FLAGS.items()]
