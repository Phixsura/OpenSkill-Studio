"""Health badge generator — generate health status badges for READMEs."""

from html import escape as html_escape
from urllib.parse import quote


def generate_health_badge(*, app_name: str, status: str, uptime_pct: float) -> dict:
    colors = {"healthy": "#22c55e", "degraded": "#eab308", "down": "#ef4444"}
    color = colors.get(status, "#6b7280")
    url_name = quote(app_name.replace("-", "--"), safe="")
    url_status = quote(status.replace("-", "--"), safe="")
    badge_url = f"https://img.shields.io/badge/{url_name}-{url_status}-{color[1:]}"
    attr_url = html_escape(badge_url, quote=True)
    attr_name = html_escape(app_name, quote=True)
    markdown = f"![{html_escape(app_name)}]({badge_url})"
    html_tag = f'<img src="{attr_url}" alt="{attr_name} Status" />'
    return {
        "badge_url": badge_url,
        "markdown": markdown,
        "html": html_tag,
        "status": status,
        "uptime_pct": uptime_pct,
        "color": color,
    }
