"""Social sharing — generate share links and embeds for marketplace apps."""

from html import escape
from urllib.parse import quote, urlencode


def build_share_links(*, app: dict, base_url: str = "https://openskill.dev") -> dict:
    slug = quote(str(app.get("slug", app["id"])), safe="")
    name = str(app.get("name", ""))
    url = f"{base_url}/marketplace/apps/{slug}"
    text = f"Check out {name} on OpenSkill Marketplace"
    twitter_params = urlencode({"text": text, "url": url})
    linkedin_params = urlencode({"url": url})
    embed = (f'<a href="{escape(url, quote=True)}">'
             f'<img src="{escape(base_url + "/badge/" + slug + ".svg", quote=True)}" '
             f'alt="{escape(name, quote=True)}" /></a>')
    return {
        "url": url,
        "twitter": f"https://twitter.com/intent/tweet?{twitter_params}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?{linkedin_params}",
        "copy_text": f"{text}\n{url}",
        "embed_badge": embed,
    }


def track_share(*, app_id: str, platform: str, user_id: str | None = None) -> dict:
    return {"app_id": app_id, "platform": platform, "user_id": user_id, "tracked": True}


def get_share_stats(*, shares: list[dict]) -> dict:
    by_platform = {}
    for s in shares:
        p = s.get("platform", "unknown")
        by_platform[p] = by_platform.get(p, 0) + 1
    return {"total": len(shares), "by_platform": by_platform}
