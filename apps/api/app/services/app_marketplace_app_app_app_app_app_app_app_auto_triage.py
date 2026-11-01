"""Incident auto-triage — automatically triage and route incidents."""
from __future__ import annotations

TRIAGE_RULES = {
    "database": {"team": "data-eng", "severity": "critical", "escalate": True},
    "api_error": {"team": "platform", "severity": "high", "escalate": False},
    "network": {"team": "infra", "severity": "high", "escalate": True},
    "auth": {"team": "security", "severity": "critical", "escalate": True},
    "performance": {"team": "platform", "severity": "medium", "escalate": False},
    "ui": {"team": "frontend", "severity": "low", "escalate": False},
}


def auto_triage(incident_type: str, symptoms: list[str]) -> dict:
    rule = TRIAGE_RULES.get(incident_type)
    if not rule:
        return {"triaged": False, "reason": "unknown_type", "assigned_team": "oncall"}
    return {"triaged": True, "incident_type": incident_type,
            "assigned_team": rule["team"], "severity": rule["severity"],
            "escalate": rule["escalate"], "symptoms": symptoms}


def triage_stats(triages: list[dict]) -> dict:
    by_team: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for t in triages:
        by_team[t.get("assigned_team", "")] = by_team.get(t.get("assigned_team", ""), 0) + 1
        by_severity[t.get("severity", "")] = by_severity.get(t.get("severity", ""), 0) + 1
    return {"total": len(triages), "by_team": by_team, "by_severity": by_severity,
            "auto_triaged": sum(1 for t in triages if t.get("triaged"))}
