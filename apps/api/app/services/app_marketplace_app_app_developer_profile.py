"""Developer profile — public developer/publisher profile builder."""

import html
import hashlib


def build_developer_profile(*, name: str, bio: str = "", avatar_email: str = "",
                               apps_count: int = 0, total_downloads: int = 0,
                               verified: bool = False, links: dict | None = None) -> dict:
    gravatar = f"https://gravatar.com/avatar/{hashlib.md5(avatar_email.strip().lower().encode()).hexdigest()}?d=identicon&s=128"
    return {
        "name": html.escape(name),
        "bio": html.escape(bio),
        "avatar_url": gravatar,
        "apps_count": apps_count,
        "total_downloads": total_downloads,
        "downloads_display": _compact(total_downloads),
        "verified": verified,
        "links": {k: html.escape(v) for k, v in (links or {}).items()},
        "badge": "🏆 Top Publisher" if total_downloads >= 100000 else "⭐ Publisher" if apps_count >= 5 else "👤 Developer",
    }


def _compact(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)
