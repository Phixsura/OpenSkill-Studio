"""Retention analytics — cohort analysis and churn prediction for apps."""

from collections import defaultdict


def compute_retention_cohorts(*, installs: list[dict]) -> dict:
    cohorts: dict[str, dict] = defaultdict(lambda: {"installed": 0, "retained": 0, "churned": 0})
    for inst in installs:
        month = inst.get("installed_at", "")[:7]
        cohorts[month]["installed"] += 1
        if inst.get("status") == "active":
            cohorts[month]["retained"] += 1
        else:
            cohorts[month]["churned"] += 1
    result = []
    for month in sorted(cohorts.keys()):
        c = cohorts[month]
        rate = round(c["retained"] / max(c["installed"], 1) * 100, 1)
        result.append({"month": month, **c, "retention_rate": rate})
    return {"cohorts": result, "total_months": len(result)}


def predict_churn_risk(*, install: dict) -> dict:
    risk_score = 0
    factors = []
    days_since_active = install.get("days_since_last_active", 0)
    if days_since_active > 30:
        risk_score += 40
        factors.append("Inactive for 30+ days")
    if days_since_active > 14:
        risk_score += 20
        factors.append("Declining activity")
    if install.get("error_count", 0) > 10:
        risk_score += 25
        factors.append("High error rate")
    if not install.get("webhooks_configured"):
        risk_score += 15
        factors.append("No webhooks configured")
    level = "high" if risk_score >= 60 else "medium" if risk_score >= 30 else "low"
    return {"risk_score": min(100, risk_score), "level": level, "factors": factors}


def compute_net_retention(*, start_count: int, end_count: int, new_installs: int) -> dict:
    if start_count == 0:
        return {"gross_retention": 0, "net_retention": 0}
    churned = max(0, start_count + new_installs - end_count)
    gross = round((start_count - churned) / start_count * 100, 1)
    net = round(end_count / start_count * 100, 1)
    return {"gross_retention": gross, "net_retention": net, "churned": churned}
