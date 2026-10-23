"""Color palette — generate and manage app brand color palettes."""

import re

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def validate_color(*, color: str) -> dict:
    if not HEX_RE.match(color):
        return {"valid": False, "error": f"Invalid hex color: {color}"}
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return {"valid": True, "color": color, "rgb": {"r": r, "g": g, "b": b},
            "luminance": round(luminance, 3), "is_dark": luminance < 0.5}


def generate_palette(*, primary: str, count: int = 5) -> dict:
    v = validate_color(color=primary)
    if not v["valid"]:
        return {"error": v["error"]}
    r, g, b = v["rgb"]["r"], v["rgb"]["g"], v["rgb"]["b"]
    shades = []
    for i in range(count):
        factor = 0.3 + (i / (count - 1)) * 0.7 if count > 1 else 1.0
        shade = f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
        shades.append({"shade": i * 100 + 100, "color": shade})
    return {"primary": primary, "palette": shades, "count": count}


def check_contrast(*, fg: str, bg: str) -> dict:
    fv = validate_color(color=fg)
    bv = validate_color(color=bg)
    if not fv["valid"] or not bv["valid"]:
        return {"error": "Invalid colors"}
    l1 = max(fv["luminance"], bv["luminance"]) + 0.05
    l2 = min(fv["luminance"], bv["luminance"]) + 0.05
    ratio = round(l1 / l2, 2)
    return {"ratio": ratio, "aa_normal": ratio >= 4.5, "aa_large": ratio >= 3.0,
            "aaa_normal": ratio >= 7.0}
