"""Changelog feed — RSS/Atom-style feed for app updates."""

from datetime import datetime, timezone


def build_changelog_feed(*, app: dict, versions: list[dict], base_url: str = "https://openskill.dev") -> dict:
    entries = []
    for v in versions:
        entries.append({
            "title": f"{app['name']} v{v['version']}",
            "link": f"{base_url}/marketplace/apps/{app['slug']}/changelog#{v['version']}",
            "published": v.get("released_at", datetime.now(timezone.utc).isoformat()),
            "summary": v.get("release_notes", "No release notes"),
            "version": v["version"],
        })
    return {
        "feed_title": f"{app['name']} Changelog",
        "feed_link": f"{base_url}/marketplace/apps/{app['slug']}/changelog",
        "entries": entries,
        "updated": entries[0]["published"] if entries else None,
    }


def render_rss(*, feed: dict) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0">', "  <channel>",
             f"    <title>{feed['feed_title']}</title>", f"    <link>{feed['feed_link']}</link>"]
    for e in feed["entries"]:
        lines.extend(["    <item>", f"      <title>{e['title']}</title>",
                       f"      <link>{e['link']}</link>", f"      <description>{e['summary']}</description>",
                       "    </item>"])
    lines.extend(["  </channel>", "</rss>"])
    return "\n".join(lines)
