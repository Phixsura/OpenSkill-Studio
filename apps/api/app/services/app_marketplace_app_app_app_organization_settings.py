"""App organization settings — org-level configuration page."""

import html

SETTING_GROUPS = {
    "general": {"label": "General", "icon": "⚙️", "settings": [
        {"key": "org_name", "label": "Organization Name", "type": "text"},
        {"key": "slug", "label": "URL Slug", "type": "text"},
        {"key": "avatar", "label": "Avatar", "type": "image"},
    ]},
    "security": {"label": "Security", "icon": "🔒", "settings": [
        {"key": "two_factor", "label": "Require 2FA", "type": "toggle"},
        {"key": "sso", "label": "SSO/SAML", "type": "toggle"},
        {"key": "ip_allowlist", "label": "IP Allowlist", "type": "toggle"},
    ]},
    "billing": {"label": "Billing", "icon": "💳", "settings": [
        {"key": "plan", "label": "Current Plan", "type": "display"},
        {"key": "payment_method", "label": "Payment Method", "type": "display"},
    ]},
}


def build_org_settings(*, org: dict) -> dict:
    groups = []
    for gid, info in SETTING_GROUPS.items():
        settings = []
        for s in info["settings"]:
            settings.append({**s, "value": org.get(s["key"]),
                              "label": html.escape(s["label"])})
        groups.append({"id": gid, "label": info["label"], "icon": info["icon"],
                        "settings": settings, "count": len(settings)})
    return {"groups": groups, "group_count": len(groups),
            "org_name": html.escape(org.get("org_name", ""))}
