"""Health badge generator — generate health status badges for READMEs."""

from xml.sax.saxutils import escape


def generate_health_badge(*, app_name: str, status: str, uptime_pct: float) -> dict:
    colors = {"healthy": "#22c55e", "degraded": "#eab308", "down": "#ef4444"}
    color = colors.get(status, "#6b7280")
    safe_name = escape(app_name)
    safe_status = escape(status)
    badge_url = f"https://img.shields.io/badge/{safe_name}-{safe_status}-{color[1:]}"
    markdown = f"![{safe_name} Status]({badge_url})"
    html_tag = f'<img src="{badge_url}" alt="{safe_name} Status" />'
    return {
        "badge_url": badge_url,
        "markdown": markdown,
        "html": html_tag,
        "status": status,
        "uptime_pct": uptime_pct,
        "color": color,
    }
