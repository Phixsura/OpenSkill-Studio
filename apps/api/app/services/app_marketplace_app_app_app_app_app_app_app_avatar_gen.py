"""Avatar generator — generate initials-based avatars with deterministic colors."""
from __future__ import annotations
import hashlib

COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
          "#EC4899", "#06B6D4", "#F97316", "#14B8A6", "#6366F1"]


def generate_avatar(*, name: str, size: int = 40) -> dict:
    initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
    color_idx = int(hashlib.md5(name.encode()).hexdigest()[:2], 16) % len(COLORS)
    bg = COLORS[color_idx]
    return {
        "initials": initials, "bg_color": bg, "size": size,
        "font_size": size // 2.5,
        "svg": (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">'
                f'<rect width="{size}" height="{size}" rx="{size//2}" fill="{bg}"/>'
                f'<text x="50%" y="50%" dy=".35em" fill="#fff" font-size="{int(size/2.5)}" '
                f'text-anchor="middle" font-family="sans-serif">{initials}</text></svg>'),
    }


def generate_group_avatars(names: list[str], *, size: int = 32, max_show: int = 5) -> dict:
    avatars = [generate_avatar(name=n, size=size) for n in names[:max_show]]
    remaining = max(0, len(names) - max_show)
    return {"avatars": avatars, "remaining": remaining,
            "remaining_display": f"+{remaining}" if remaining else "",
            "total": len(names)}
