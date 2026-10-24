"""Log retention policy — manage log retention and cleanup."""
from __future__ import annotations


def create_policy(name: str, retention_days: int, sources: list[str],
                   max_size_gb: float = 0) -> dict:
    return {"name": name, "retention_days": retention_days, "sources": sources,
            "max_size_gb": max_size_gb, "status": "active"}


def evaluate_retention(policies: list[dict], current_usage: dict[str, dict]) -> dict:
    actions = []
    total_reclaimable_gb = 0
    for policy in policies:
        for source in policy["sources"]:
            usage = current_usage.get(source, {})
            oldest_days = usage.get("oldest_days", 0)
            size_gb = usage.get("size_gb", 0)
            if oldest_days > policy["retention_days"]:
                reclaimable = round(size_gb * (oldest_days - policy["retention_days"]) / max(oldest_days, 1), 2)
                total_reclaimable_gb += reclaimable
                actions.append({"source": source, "policy": policy["name"],
                                 "action": "purge", "reclaimable_gb": reclaimable,
                                 "days_over": oldest_days - policy["retention_days"]})
    return {"actions": actions, "action_count": len(actions),
            "total_reclaimable_gb": round(total_reclaimable_gb, 2)}
