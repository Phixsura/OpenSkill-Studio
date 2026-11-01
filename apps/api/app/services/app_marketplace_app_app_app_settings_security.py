"""App settings security — security settings page builder."""

import html


def build_security_settings(*, settings: dict) -> dict:
    items = [
        {"key": "two_factor", "label": "Two-Factor Authentication", "icon": "🔐",
         "description": "Require 2FA for all team members",
         "enabled": settings.get("two_factor", False), "type": "toggle"},
        {"key": "sso", "label": "SSO / SAML", "icon": "🔑",
         "description": "Enable single sign-on",
         "enabled": settings.get("sso", False), "type": "toggle"},
        {"key": "ip_allowlist", "label": "IP Allowlist", "icon": "🌐",
         "description": "Restrict access by IP address",
         "enabled": settings.get("ip_allowlist", False), "type": "toggle"},
        {"key": "audit_log", "label": "Audit Log", "icon": "📋",
         "description": "Track all user actions",
         "enabled": settings.get("audit_log", True), "type": "toggle"},
        {"key": "session_timeout", "label": "Session Timeout", "icon": "⏰",
         "description": "Auto-logout after inactivity",
         "value": settings.get("session_timeout_min", 30), "type": "number", "unit": "minutes"},
    ]
    enabled_count = sum(1 for i in items if i.get("enabled") or i.get("type") == "number")
    score = round(enabled_count / len(items) * 100)
    return {"settings": items, "total": len(items), "security_score": score,
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C"}
