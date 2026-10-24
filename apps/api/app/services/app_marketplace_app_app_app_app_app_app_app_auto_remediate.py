"""Auto-remediation engine — automatically fix common issues."""
from __future__ import annotations


PLAYBOOKS = {
    "high_cpu": {"action": "scale_up", "description": "Add replicas when CPU > 90%"},
    "disk_full": {"action": "cleanup_logs", "description": "Purge old logs when disk > 85%"},
    "connection_pool_exhausted": {"action": "increase_pool", "description": "Expand pool size"},
    "high_error_rate": {"action": "rollback", "description": "Rollback last deploy"},
    "certificate_expiring": {"action": "renew_cert", "description": "Auto-renew TLS certificate"},
}


def evaluate_remediation(issue_type: str, severity: str) -> dict:
    playbook = PLAYBOOKS.get(issue_type)
    if not playbook:
        return {"can_remediate": False, "reason": "no_playbook"}
    auto_approve = severity != "critical"  # critical needs human approval
    return {"can_remediate": True, "issue": issue_type, "severity": severity,
            "action": playbook["action"], "description": playbook["description"],
            "auto_approve": auto_approve}


def remediation_stats(actions: list[dict]) -> dict:
    auto = sum(1 for a in actions if a.get("auto_approve"))
    manual = len(actions) - auto
    by_action: dict[str, int] = {}
    for a in actions:
        by_action[a.get("action", "")] = by_action.get(a.get("action", ""), 0) + 1
    return {"total": len(actions), "auto": auto, "manual": manual,
            "by_action": by_action, "auto_pct": round(auto / max(len(actions), 1) * 100)}
