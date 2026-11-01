"""Install confirmation — pre-install confirmation with permission review."""


def build_install_confirmation(*, app_name: str, permissions: list[dict],
                                  price: float = 0) -> dict:
    risk_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    max_risk = "low"
    for p in permissions:
        risk = p.get("risk", "low")
        if risk_levels.get(risk, 0) > risk_levels.get(max_risk, 0):
            max_risk = risk
    return {
        "app_name": app_name,
        "permissions": permissions,
        "permission_count": len(permissions),
        "price_label": "Free" if price == 0 else f"${price:.2f}/mo",
        "max_risk": max_risk,
        "requires_review": max_risk in ("high", "critical"),
        "confirm_message": f"Install {app_name}?" if max_risk == "low" else
                            f"⚠️ {app_name} requests {max_risk}-risk permissions. Review carefully.",
    }
