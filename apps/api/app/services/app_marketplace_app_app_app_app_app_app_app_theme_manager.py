"""Platform theme manager — manage UI themes with color tokens."""
from __future__ import annotations
import re


PRESETS = {
    "light": {"bg": "#FFFFFF", "fg": "#1F2937", "primary": "#3B82F6",
              "secondary": "#6B7280", "accent": "#8B5CF6", "success": "#10B981",
              "warning": "#F59E0B", "error": "#EF4444"},
    "dark": {"bg": "#111827", "fg": "#F9FAFB", "primary": "#60A5FA",
             "secondary": "#9CA3AF", "accent": "#A78BFA", "success": "#34D399",
             "warning": "#FBBF24", "error": "#F87171"},
    "midnight": {"bg": "#0F172A", "fg": "#E2E8F0", "primary": "#818CF8",
                  "secondary": "#94A3B8", "accent": "#C084FC", "success": "#4ADE80",
                  "warning": "#FCD34D", "error": "#FB923C"},
}

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def get_theme(name: str) -> dict:
    colors = PRESETS.get(name)
    if not colors:
        return {"error": f"Unknown theme: {name}"}
    return {"name": name, "colors": colors, "token_count": len(colors)}


def validate_color(value: str) -> bool:
    return bool(HEX_RE.match(value))


def create_custom_theme(*, name: str, base: str = "light",
                          overrides: dict[str, str]) -> dict:
    base_colors = dict(PRESETS.get(base, PRESETS["light"]))
    invalid = [k for k, v in overrides.items() if not validate_color(v)]
    if invalid:
        return {"error": f"Invalid hex colors for: {', '.join(invalid)}"}
    base_colors.update(overrides)
    return {"name": name, "base": base, "colors": base_colors,
            "overrides_count": len(overrides)}


def list_presets() -> list[dict]:
    return [{"name": k, "token_count": len(v), "preview_bg": v["bg"],
             "preview_primary": v["primary"]} for k, v in PRESETS.items()]
