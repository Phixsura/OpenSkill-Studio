"""Usage quota enforcement — real-time enforcement and grace periods."""


def enforce_quota(*, resource: str, current: int, limit: int,
                    grace_pct: float = 10.0) -> dict:
    if limit <= 0:
        return {"action": "allow", "unlimited": True, "resource": resource}
    usage_pct = round(current / limit * 100, 1)
    grace_limit = int(limit * (1 + grace_pct / 100))
    if current < limit:
        return {"action": "allow", "resource": resource, "usage_pct": usage_pct,
                "remaining": limit - current, "warning": usage_pct >= 80}
    elif current < grace_limit:
        overage = current - limit
        return {"action": "warn", "resource": resource, "usage_pct": usage_pct,
                "overage": overage, "grace_remaining": grace_limit - current,
                "message": f"Over quota by {overage}. Grace period active."}
    else:
        return {"action": "block", "resource": resource, "usage_pct": usage_pct,
                "overage": current - limit,
                "message": "Quota exceeded. Upgrade your plan to continue."}


def get_enforcement_summary(*, quotas: list[dict]) -> dict:
    results = [enforce_quota(resource=q["resource"], current=q["current"], limit=q["limit"])
               for q in quotas]
    blocked = sum(1 for r in results if r["action"] == "block")
    warned = sum(1 for r in results if r["action"] == "warn")
    return {"results": results, "blocked_count": blocked, "warned_count": warned,
            "all_ok": blocked == 0 and warned == 0}
