"""Complete developer settings — all developer account settings in one page."""


def build_complete_developer_settings(*, profile: dict, security: dict, notifications: dict,
                                          api_keys: list[dict], connected_accounts: list[dict],
                                          data_export: dict | None) -> dict:
    return {
        "page_type": "developer_settings",
        "tabs": [
            {"key": "profile", "title": "Profile", "icon": "👤", "data": {
                "name": profile.get("display_name"), "slug": profile.get("slug"),
                "email": profile.get("email"), "bio": profile.get("bio"),
                "completeness": profile.get("completeness_pct", 0)}},
            {"key": "security", "title": "Security", "icon": "🔒", "data": {
                "two_factor": security.get("2fa_enabled", False),
                "sessions": security.get("active_sessions", 0),
                "last_password_change": security.get("last_password_change")}},
            {"key": "notifications", "title": "Notifications", "icon": "🔔", "data": notifications},
            {"key": "api_keys", "title": f"API Keys ({len(api_keys)})", "icon": "🔑",
             "data": {"keys": api_keys}},
            {"key": "connected", "title": f"Connected ({len(connected_accounts)})", "icon": "🔗",
             "data": {"accounts": connected_accounts}},
            {"key": "data", "title": "Data & Privacy", "icon": "📋",
             "data": {"export_available": data_export is not None, "last_export": data_export}},
            {"key": "danger", "title": "Danger Zone", "icon": "⚠️",
             "data": {"actions": ["change_slug", "disable_account", "delete_account"]}},
        ],
        "tab_count": 7,
    }
