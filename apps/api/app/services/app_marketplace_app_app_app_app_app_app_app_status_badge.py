"""Platform status badge generator — SVG status badges for README and dashboards."""
from __future__ import annotations
import html


def generate_badge(*, label: str, value: str, color: str = "green") -> dict:
    safe_label = html.escape(label)
    safe_value = html.escape(value)
    colors = {"green": "#22C55E", "yellow": "#EAB308", "red": "#EF4444",
              "blue": "#3B82F6", "gray": "#6B7280", "purple": "#8B5CF6"}
    hex_color = colors.get(color, colors["gray"])
    label_width = len(safe_label) * 7 + 10
    value_width = len(safe_value) * 7 + 10
    total_width = label_width + value_width
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">'
           f'<rect width="{label_width}" height="20" fill="#555"/>'
           f'<rect x="{label_width}" width="{value_width}" height="20" fill="{hex_color}"/>'
           f'<text x="{label_width // 2}" y="14" fill="#fff" text-anchor="middle" font-size="11">{safe_label}</text>'
           f'<text x="{label_width + value_width // 2}" y="14" fill="#fff" text-anchor="middle" font-size="11">{safe_value}</text>'
           f'</svg>')
    return {"svg": svg, "label": safe_label, "value": safe_value,
            "color": hex_color, "width": total_width, "content_type": "image/svg+xml"}


def generate_status_badge(*, status: str, uptime_pct: float | None = None) -> dict:
    if status == "operational":
        return generate_badge(label="status", value="operational", color="green")
    elif status == "degraded":
        return generate_badge(label="status", value="degraded", color="yellow")
    elif status == "outage":
        return generate_badge(label="status", value="outage", color="red")
    return generate_badge(label="status", value=status, color="gray")


def generate_uptime_badge(uptime_pct: float) -> dict:
    color = "green" if uptime_pct >= 99.9 else "yellow" if uptime_pct >= 99 else "red"
    return generate_badge(label="uptime", value=f"{uptime_pct}%", color=color)
