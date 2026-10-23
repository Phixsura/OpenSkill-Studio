"""Social sharing — generate share links and embeds for marketplace apps."""


def build_share_links(*, app: dict, base_url: str = "https://openskill.dev") -> dict:
    url = f"{base_url}/marketplace/apps/{app.get('slug', app['id'])}"
    name = app.get("name", "")
    text = f"Check out {name} on OpenSkill Marketplace"
    return {
        "url": url,
        "twitter": f"https://twitter.com/intent/tweet?text={text}&url={url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={url}",
        "copy_text": f"{text}\n{url}",
        "embed_badge": f'<a href="{url}"><img src="{base_url}/badge/{app.get("slug")}.svg" alt="{name}" /></a>',
    }


def track_share(*, app_id: str, platform: str, user_id: str | None = None) -> dict:
    return {"app_id": app_id, "platform": platform, "user_id": user_id, "tracked": True}


def get_share_stats(*, shares: list[dict]) -> dict:
    by_platform = {}
    for s in shares:
        p = s.get("platform", "unknown")
        by_platform[p] = by_platform.get(p, 0) + 1
    return {"total": len(shares), "by_platform": by_platform}
