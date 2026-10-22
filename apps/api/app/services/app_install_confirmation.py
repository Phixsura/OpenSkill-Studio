"""Install confirmation — build install confirmation data for consent screen."""


def build_install_confirmation(*, app: dict, permissions: list[str], org_name: str) -> dict:
    high_risk = [p for p in permissions if p.startswith("write:") or p in ("run:background_jobs",)]
    return {
        "app_name": app.get("name"),
        "developer_name": app.get("developer_name"),
        "developer_verified": app.get("developer_verified", False),
        "org_name": org_name,
        "permissions": permissions,
        "high_risk_permissions": high_risk,
        "has_high_risk": len(high_risk) > 0,
        "total_permissions": len(permissions),
    }
