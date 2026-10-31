"""Accessibility checker — validate UI components against WCAG guidelines."""
from __future__ import annotations


def check_color_contrast(*, fg: str, bg: str, font_size: int = 16,
                           is_bold: bool = False) -> dict:
    # Simplified contrast check using hex luminance
    def hex_lum(color: str) -> float:
        h = color.lstrip("#")
        r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
        def lin(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    l1 = max(hex_lum(fg), hex_lum(bg))
    l2 = min(hex_lum(fg), hex_lum(bg))
    ratio = round((l1 + 0.05) / (l2 + 0.05), 2)
    large_text = font_size >= 18 or (font_size >= 14 and is_bold)
    aa = ratio >= 3.0 if large_text else ratio >= 4.5
    aaa = ratio >= 4.5 if large_text else ratio >= 7.0
    return {"ratio": ratio, "aa": aa, "aaa": aaa, "large_text": large_text,
            "level": "AAA" if aaa else "AA" if aa else "Fail"}


def check_component(component: dict) -> dict:
    issues = []
    if not component.get("aria_label") and not component.get("label"):
        issues.append({"rule": "label", "severity": "error", "message": "Missing accessible label"})
    if component.get("type") == "image" and not component.get("alt"):
        issues.append({"rule": "alt_text", "severity": "error", "message": "Missing alt text"})
    if component.get("type") == "button" and not component.get("label"):
        issues.append({"rule": "button_label", "severity": "error", "message": "Button missing label"})
    if component.get("focusable") is False:
        issues.append({"rule": "focusable", "severity": "warning", "message": "Not keyboard focusable"})
    return {"component": component.get("name", ""), "issues": issues,
            "issue_count": len(issues), "passes": len(issues) == 0}
