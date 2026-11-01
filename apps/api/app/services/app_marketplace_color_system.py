"""Color system — design token management for marketplace UI consistency."""

COLOR_TOKENS = {
    "primary": {"50": "#eff6ff", "500": "#3b82f6", "600": "#2563eb", "700": "#1d4ed8"},
    "success": {"50": "#f0fdf4", "500": "#22c55e", "600": "#16a34a", "700": "#15803d"},
    "warning": {"50": "#fffbeb", "500": "#f59e0b", "600": "#d97706", "700": "#b45309"},
    "danger": {"50": "#fef2f2", "500": "#ef4444", "600": "#dc2626", "700": "#b91c1c"},
    "neutral": {"50": "#f9fafb", "100": "#f3f4f6", "200": "#e5e7eb", "500": "#6b7280", "700": "#374151", "900": "#111827"},
}

STATUS_COLORS = {
    "operational": "success", "degraded": "warning", "outage": "danger",
    "published": "success", "draft": "neutral", "in_review": "warning",
    "active": "success", "inactive": "neutral", "suspended": "danger",
}


def get_status_color(*, status: str) -> dict:
    color_key = STATUS_COLORS.get(status, "neutral")
    tokens = COLOR_TOKENS.get(color_key, COLOR_TOKENS["neutral"])
    return {"status": status, "color_key": color_key, "bg": tokens.get("50", "#f9fafb"),
            "text": tokens.get("700", "#374151"), "badge": tokens.get("500", "#6b7280")}


def get_color_palette() -> dict:
    return COLOR_TOKENS


def generate_css_custom_properties() -> dict:
    props = {}
    for group, shades in COLOR_TOKENS.items():
        for shade, value in shades.items():
            props[f"--color-{group}-{shade}"] = value
    return props
