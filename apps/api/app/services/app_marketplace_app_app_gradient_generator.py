"""Gradient generator — CSS gradient builder with presets."""

import re

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

PRESETS = {
    "sunset": {"from": "#F97316", "to": "#EC4899", "direction": "to right"},
    "ocean": {"from": "#3B82F6", "to": "#06B6D4", "direction": "to right"},
    "forest": {"from": "#22C55E", "to": "#14B8A6", "direction": "to bottom right"},
    "midnight": {"from": "#1E1B4B", "to": "#312E81", "direction": "to bottom"},
    "fire": {"from": "#EF4444", "to": "#F59E0B", "direction": "to right"},
    "lavender": {"from": "#8B5CF6", "to": "#EC4899", "direction": "to right"},
}


def generate_gradient(*, from_color: str, to_color: str,
                        direction: str = "to right", via_color: str | None = None) -> dict:
    errors = []
    for c in [from_color, to_color] + ([via_color] if via_color else []):
        if not HEX_RE.match(c):
            errors.append(f"Invalid color: {c}")
    if errors:
        return {"valid": False, "errors": errors}
    stops = [from_color]
    if via_color:
        stops.append(via_color)
    stops.append(to_color)
    css = f"linear-gradient({direction}, {', '.join(stops)})"
    return {"valid": True, "css": css, "stops": stops, "direction": direction}


def list_presets() -> list[dict]:
    return [{"id": k, **v, "css": f"linear-gradient({v['direction']}, {v['from']}, {v['to']})"}
            for k, v in PRESETS.items()]
