"""Color palette generator — create accessible color palettes from a base color."""
from __future__ import annotations


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_shades(base: str, *, steps: int = 10) -> list[dict]:
    r, g, b = hex_to_rgb(base)
    shades = []
    for i in range(steps):
        factor = i / (steps - 1)  # 0 (lightest) to 1 (darkest)
        lr = int(255 - (255 - r) * factor)
        lg = int(255 - (255 - g) * factor)
        lb = int(255 - (255 - b) * factor)
        shade = (steps - i) * 100  # 1000 to 100
        shades.append({"shade": shade, "hex": rgb_to_hex(lr, lg, lb),
                         "rgb": f"rgb({lr},{lg},{lb})"})
    return shades


def check_contrast(fg: str, bg: str) -> dict:
    fr, fg_g, fb = hex_to_rgb(fg)
    br, bg_g, bb = hex_to_rgb(bg)
    def lum(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    l1 = 0.2126 * lum(fr) + 0.7152 * lum(fg_g) + 0.0722 * lum(fb)
    l2 = 0.2126 * lum(br) + 0.7152 * lum(bg_g) + 0.0722 * lum(bb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    ratio = round((lighter + 0.05) / (darker + 0.05), 2)
    return {"ratio": ratio, "aa_normal": ratio >= 4.5, "aa_large": ratio >= 3.0,
            "aaa_normal": ratio >= 7.0}
