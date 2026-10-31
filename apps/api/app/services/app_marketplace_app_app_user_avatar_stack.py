"""User avatar stack — overlapping avatar display for user groups."""

import hashlib


COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899"]


def build_avatar_stack(*, users: list[dict], max_display: int = 5) -> dict:
    displayed = users[:max_display]
    remaining = max(len(users) - max_display, 0)
    avatars = []
    for u in displayed:
        name = u.get("name", "?")
        initials = "".join(w[0].upper() for w in name.split()[:2])
        idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(COLORS)
        avatars.append({"name": name, "initials": initials, "color": COLORS[idx],
                         "image": u.get("avatar_url")})
    return {"avatars": avatars, "remaining": remaining, "total": len(users),
            "show_remaining": remaining > 0,
            "remaining_label": f"+{remaining}" if remaining > 0 else ""}
