"""Avatar generator — generate default avatars from names."""

import hashlib


COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6",
           "#ec4899", "#06b6d4", "#f97316", "#6366f1", "#14b8a6"]


def generate_avatar(*, name: str, size: int = 64) -> dict:
    initials = "".join(word[0].upper() for word in name.split()[:2]) or "?"
    color_idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(COLORS)
    bg_color = COLORS[color_idx]
    return {
        "initials": initials,
        "bg_color": bg_color,
        "text_color": "#ffffff",
        "size": size,
        "font_size": size // 2,
    }


def generate_app_icon(*, app_name: str, category: str | None = None) -> dict:
    cat_icons = {"tools": "🔧", "design": "🎨", "security": "🔒", "analytics": "📊",
                  "communication": "💬", "development": "💻", "productivity": "📋"}
    icon = cat_icons.get(category, app_name[0].upper() if app_name else "?")
    avatar = generate_avatar(name=app_name)
    return {**avatar, "category_icon": icon, "has_category_icon": category in cat_icons}
