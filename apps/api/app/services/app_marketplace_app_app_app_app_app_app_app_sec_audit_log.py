"""Security audit logger — log and query security events."""
from __future__ import annotations
import html
import time

_audit_log: list[dict] = []


def log_security_event(actor: str, action: str, resource: str,
                        result: str = "success", ip: str = "") -> dict:
    entry = {"actor": html.escape(actor), "action": action,
             "resource": html.escape(resource), "result": result,
             "ip": ip, "timestamp": time.time(),
             "severity": "high" if action in ("login_failed", "permission_denied", "token_revoked") else "info"}
    _audit_log.append(entry)
    return entry


def query_audit_log(actor: str | None = None, action: str | None = None,
                     severity: str | None = None, limit: int = 50) -> dict:
    filtered = _audit_log
    if actor:
        filtered = [e for e in filtered if e["actor"] == actor]
    if action:
        filtered = [e for e in filtered if e["action"] == action]
    if severity:
        filtered = [e for e in filtered if e["severity"] == severity]
    recent = list(reversed(filtered[-limit:]))
    return {"events": recent, "total": len(filtered), "shown": len(recent)}


def audit_summary() -> dict:
    by_action: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for e in _audit_log:
        by_action[e["action"]] = by_action.get(e["action"], 0) + 1
        by_severity[e["severity"]] = by_severity.get(e["severity"], 0) + 1
    return {"total": len(_audit_log), "by_action": by_action, "by_severity": by_severity}


def clear_audit_log() -> None:
    _audit_log.clear()
