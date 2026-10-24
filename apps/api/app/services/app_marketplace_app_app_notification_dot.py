"""Notification dot — simple notification indicator."""


def build_notification_dot(*, count: int, max_display: int = 9, color: str = "red") -> dict:
    return {
        "count": count,
        "display": f"{max_display}+" if count > max_display else str(count),
        "visible": count > 0,
        "color": color,
        "size": "sm" if count < 10 else "md",
        "aria_label": f"{count} notifications",
    }
