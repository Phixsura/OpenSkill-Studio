"""Count badge — notification count badge generator."""


def build_count_badge(*, count: int, max_display: int = 99) -> dict:
    display = f"{max_display}+" if count > max_display else str(count)
    size = "sm" if count < 10 else "md" if count < 100 else "lg"
    return {
        "count": count,
        "display": display,
        "visible": count > 0,
        "size": size,
        "urgency": "high" if count >= 10 else "medium" if count >= 3 else "low",
    }
