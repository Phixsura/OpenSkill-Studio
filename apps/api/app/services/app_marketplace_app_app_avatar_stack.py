"""Avatar stack — overlapping user avatar display."""

import hashlib
import html


def build_avatar_stack(*, users: list[dict], max_display: int = 5) -> dict:
    visible = users[:max_display]
    overflow = max(0, len(users) - max_display)
    avatars = []
    for u in visible:
        name = html.escape(u.get("name", "?"))
        email = u.get("email", "").strip().lower()
        gravatar = f"https://gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=identicon&s=32"
        initials = "".join(w[0].upper() for w in name.split()[:2]) if name != "?" else "?"
        avatars.append({"name": name, "initials": initials, "avatar_url": u.get("avatar_url") or gravatar})
    return {"avatars": avatars, "overflow_count": overflow,
            "overflow_text": f"+{overflow}" if overflow else None,
            "total": len(users)}
