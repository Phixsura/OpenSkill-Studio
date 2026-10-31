"""Icon generator — generate placeholder icons and validate app icons."""

import hashlib


def generate_placeholder_icon(*, app_name: str, size: int = 64) -> dict:
    colors = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#f97316"]
    color_idx = int(hashlib.md5(app_name.encode()).hexdigest(), 16) % len(colors)
    initial = app_name[0].upper() if app_name else "?"
    return {"type": "placeholder", "initial": initial, "bg_color": colors[color_idx],
            "text_color": "#ffffff", "size": size}


def validate_icon(*, width: int, height: int, format: str, size_bytes: int) -> dict:
    errors = []
    if width != height:
        errors.append("Icon must be square")
    if width < 128:
        errors.append("Minimum size is 128x128")
    if width > 1024:
        errors.append("Maximum size is 1024x1024")
    if format not in ("png", "svg", "webp"):
        errors.append(f"Unsupported format: {format}")
    if size_bytes > 512 * 1024:
        errors.append("Maximum file size is 512KB")
    return {"valid": len(errors) == 0, "errors": errors}


def get_icon_requirements() -> dict:
    return {"min_size": 128, "max_size": 1024, "formats": ["png", "svg", "webp"],
            "max_file_size_kb": 512, "must_be_square": True,
            "recommended_size": 256}
