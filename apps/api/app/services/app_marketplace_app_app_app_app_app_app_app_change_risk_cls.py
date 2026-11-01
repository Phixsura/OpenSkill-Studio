"""API change risk classifier — classify change risk by type and scope."""
from __future__ import annotations


def classify_change_risk(change: dict) -> dict:
    risk_score = 0
    tags = []
    change_type = change.get("type", "")
    if change_type == "schema_change":
        risk_score += 30; tags.append("schema")
    elif change_type == "endpoint_removal":
        risk_score += 40; tags.append("breaking")
    elif change_type == "new_endpoint":
        risk_score += 5; tags.append("additive")
    elif change_type == "config_change":
        risk_score += 15; tags.append("config")
    if change.get("affects_auth"):
        risk_score += 25; tags.append("auth")
    consumers = change.get("consumers", 0)
    if consumers > 50:
        risk_score += 20; tags.append("high_impact")
    elif consumers > 10:
        risk_score += 10; tags.append("moderate_impact")
    risk_score = min(100, risk_score)
    level = "critical" if risk_score >= 70 else ("high" if risk_score >= 40 else ("medium" if risk_score >= 20 else "low"))
    return {"score": risk_score, "level": level, "tags": tags}
