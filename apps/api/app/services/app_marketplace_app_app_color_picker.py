"""Color picker — brand color selection with presets."""

import re

PRESETS = {
    "blue": "#3B82F6", "green": "#10B981", "red": "#EF4444",
    "purple": "#8B5CF6", "orange": "#F97316", "pink": "#EC4899",
    "teal": "#14B8A6", "indigo": "#6366F1",
}

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def validate_color(value: str) -> dict:
    if value in PRESETS:
        return {"valid": True, "hex": PRESETS[value], "source": "preset", "name": value}
    if HEX_RE.match(value):
        return {"valid": True, "hex": value.upper(), "source": "custom", "name": None}
    return {"valid": False, "hex": None, "source": None, "name": None,
            "error": "Invalid color. Use a preset name or #RRGGBB hex."}


def get_presets() -> list[dict]:
    return [{"name": k, "hex": v} for k, v in PRESETS.items()]
