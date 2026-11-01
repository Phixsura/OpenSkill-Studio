"""Theme config — app theming with color tokens and font settings."""

import re
import html

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
FONT_FAMILIES = ["Inter", "Roboto", "Fira Code", "Poppins", "Open Sans", "System Default"]


def build_theme_config(*, primary: str = "#3B82F6", secondary: str = "#6366F1",
                        background: str = "#FFFFFF", text: str = "#111827",
                        font: str = "Inter", border_radius: int = 8) -> dict:
    colors = {"primary": primary, "secondary": secondary, "background": background, "text": text}
    errors = []
    for name, val in colors.items():
        if not HEX_RE.match(val):
            errors.append(f"Invalid {name} color: {val}")
    if font not in FONT_FAMILIES:
        errors.append(f"Unknown font: {font}")
    if not (0 <= border_radius <= 24):
        errors.append("border_radius must be 0-24")
    return {"colors": colors, "font": font, "border_radius": border_radius,
            "valid": len(errors) == 0, "errors": errors,
            "css_vars": {f"--color-{k}": v for k, v in colors.items()},
            "available_fonts": FONT_FAMILIES}
