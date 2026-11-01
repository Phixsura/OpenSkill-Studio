"""Status badge generator — generate SVG status badges."""
from __future__ import annotations
import html


def generate_badge(label: str, value: str, color: str = "green") -> dict:
    safe_label = html.escape(label)
    safe_value = html.escape(value)
    colors = {"green": "#4c1", "yellow": "#dfb317", "red": "#e05d44", "blue": "#007ec6", "gray": "#555"}
    bg = colors.get(color, colors["gray"])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">'
           f'<rect width="60" height="20" fill="#555"/>'
           f'<rect x="60" width="60" height="20" fill="{bg}"/>'
           f'<text x="30" y="14" fill="#fff" text-anchor="middle" font-size="11">{safe_label}</text>'
           f'<text x="90" y="14" fill="#fff" text-anchor="middle" font-size="11">{safe_value}</text>'
           f'</svg>')
    return {"svg": svg, "label": safe_label, "value": safe_value, "color": color}


def generate_badges(metrics: dict) -> list[dict]:
    badges = []
    uptime = metrics.get("uptime_pct", 99.9)
    color = "green" if uptime >= 99.9 else "yellow" if uptime >= 99 else "red"
    badges.append(generate_badge("uptime", f"{uptime}%", color))
    version = metrics.get("version", "0.0.0")
    badges.append(generate_badge("version", f"v{version}", "blue"))
    status = metrics.get("status", "operational")
    badges.append(generate_badge("status", status, "green" if status == "operational" else "yellow"))
    return badges
