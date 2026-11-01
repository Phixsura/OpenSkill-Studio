"""Fleet Cloud WAF v9 — track cloud-native WAF rule enforcement."""
from __future__ import annotations
def fleet_cloud_waf_v9(rules: list[dict]) -> dict:
    active = [r for r in rules if r.get("active")]
    blocked = sum(r.get("blocked_today", 0) for r in rules)
    false_pos = sum(r.get("false_positives", 0) for r in rules)
    return {"rules": len(rules), "active": len(active), "blocked_today": blocked,
            "false_positives": false_pos, "healthy": false_pos == 0}
