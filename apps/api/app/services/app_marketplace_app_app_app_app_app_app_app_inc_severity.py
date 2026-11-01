"""Incident severity classifier — auto-classify incident severity."""
from __future__ import annotations


SEVERITY_RULES = {
    "critical": {"conditions": ["data_loss", "complete_outage", "security_breach"], "response_min": 15},
    "high": {"conditions": ["partial_outage", "degraded_performance", "payment_failure"], "response_min": 60},
    "medium": {"conditions": ["intermittent_errors", "slow_response", "feature_broken"], "response_min": 240},
    "low": {"conditions": ["cosmetic", "documentation", "minor_bug"], "response_min": 1440},
}


def classify_severity(symptoms: list[str]) -> dict:
    for severity, rules in SEVERITY_RULES.items():
        if any(s in rules["conditions"] for s in symptoms):
            matched = [s for s in symptoms if s in rules["conditions"]]
            return {"severity": severity, "matched_symptoms": matched,
                    "response_time_min": rules["response_min"],
                    "escalate": severity in ("critical", "high")}
    return {"severity": "low", "matched_symptoms": [], "response_time_min": 1440, "escalate": False}


def severity_distribution(incidents: list[dict]) -> dict:
    by_sev: dict[str, int] = {}
    for i in incidents:
        sev = i.get("severity", "low")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    return {"total": len(incidents), "by_severity": by_sev,
            "critical_pct": round(by_sev.get("critical", 0) / max(len(incidents), 1) * 100)}
