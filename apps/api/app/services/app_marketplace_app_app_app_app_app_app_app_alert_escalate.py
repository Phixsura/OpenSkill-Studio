"""Alert escalation policy — define escalation chains for alerts."""
from __future__ import annotations


def create_policy(name: str, levels: list[dict]) -> dict:
    items = []
    for i, lv in enumerate(levels):
        items.append({"level": i + 1, "contacts": lv.get("contacts", []),
                       "channel": lv.get("channel", "email"),
                       "wait_min": lv.get("wait_min", 5)})
    return {"name": name, "levels": items, "total_levels": len(items)}


def escalate(policy: dict, current_level: int) -> dict:
    if current_level >= policy["total_levels"]:
        return {"escalated": False, "reason": "max_level_reached",
                "current_level": current_level}
    next_lv = policy["levels"][current_level]
    return {"escalated": True, "new_level": current_level + 1,
            "contacts": next_lv["contacts"], "channel": next_lv["channel"],
            "wait_min": next_lv["wait_min"]}


def simulate_escalation(policy: dict) -> list[dict]:
    timeline = []
    elapsed = 0
    for lv in policy["levels"]:
        timeline.append({"level": lv["level"], "at_min": elapsed,
                         "contacts": lv["contacts"], "channel": lv["channel"]})
        elapsed += lv["wait_min"]
    return timeline
