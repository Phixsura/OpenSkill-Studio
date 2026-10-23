"""Developer changelog RSS v3 — aggregated RSS feed for all platform updates."""


def build_platform_rss(*, app_updates: list[dict], platform_updates: list[dict],
                          base_url: str = "https://openskill.dev") -> dict:
    entries = []
    for u in app_updates:
        entries.append({"title": f"{u['app_name']} v{u['version']}",
                          "link": f"{base_url}/marketplace/apps/{u.get('slug')}/changelog",
                          "date": u.get("released_at", ""), "type": "app_update"})
    for p in platform_updates:
        entries.append({"title": p["title"], "link": f"{base_url}/changelog",
                          "date": p.get("date", ""), "type": "platform"})
    entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    return {"title": "OpenSkill Platform Updates", "link": f"{base_url}/feed.rss",
            "entries": entries[:50], "entry_count": len(entries[:50])}


def render_rss_xml(*, feed: dict) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0">', '  <channel>',
             f'    <title>{feed["title"]}</title>', f'    <link>{feed["link"]}</link>']
    for e in feed["entries"]:
        lines.extend(['    <item>', f'      <title>{e["title"]}</title>',
                       f'      <link>{e["link"]}</link>', f'      <pubDate>{e["date"]}</pubDate>',
                       '    </item>'])
    lines.extend(['  </channel>', '</rss>'])
    return '\n'.join(lines)
