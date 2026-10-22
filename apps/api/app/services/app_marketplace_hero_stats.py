"""Marketplace hero stats — real-time stats for the hero section."""


def build_hero_stats(*, total_apps: int, total_installs: int, total_developers: int, total_executions: int) -> list[dict]:
    return [
        {"label": "Apps", "value": total_apps, "icon": "📦"},
        {"label": "Installs", "value": f"{total_installs:,}", "icon": "📥"},
        {"label": "Developers", "value": total_developers, "icon": "👩‍💻"},
        {"label": "Executions", "value": f"{total_executions:,}", "icon": "⚡"},
    ]
