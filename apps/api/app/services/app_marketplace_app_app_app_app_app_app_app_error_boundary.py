"""Error boundary handler — structured error reporting with context."""
from __future__ import annotations
import html
import hashlib


def create_error_report(*, error_type: str, message: str, stack_trace: str = "",
                          component: str = "", url: str = "",
                          user_id: str = "") -> dict:
    fingerprint = hashlib.sha256(f"{error_type}:{message}:{component}".encode()).hexdigest()[:12]
    safe_msg = html.escape(message[:500])
    return {
        "fingerprint": fingerprint,
        "error_type": error_type,
        "message": safe_msg,
        "stack_preview": stack_trace[:300] if stack_trace else "",
        "component": component,
        "url": url,
        "user_id": user_id,
        "severity": _classify(error_type),
    }


def _classify(error_type: str) -> str:
    critical = ("TypeError", "ReferenceError", "RangeError", "SyntaxError")
    if error_type in critical:
        return "critical"
    if "Network" in error_type or "Fetch" in error_type:
        return "warning"
    return "error"


def build_recovery_ui(error: dict) -> dict:
    return {
        "title": "Something went wrong",
        "message": error["message"],
        "actions": [
            {"label": "Retry", "action": "retry"},
            {"label": "Go Home", "action": "navigate", "url": "/"},
            {"label": "Report Issue", "action": "report", "fingerprint": error["fingerprint"]},
        ],
        "show_details": bool(error["stack_preview"]),
    }
