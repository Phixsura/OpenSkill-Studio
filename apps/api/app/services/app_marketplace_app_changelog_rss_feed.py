"""Changelog RSS/Atom feed — generate feeds for all marketplace updates."""

from datetime import datetime, timezone


def build_global_feed(*, updates: list[dict], base_url: str = "https://openskill.dev") -> dict:
    entries = []
    for u in updates:
        entries.append({
            "title": f"{u['app_name']} v{u['version']}",
            "link": f"{base_url}/marketplace/apps/{u['app_slug']}/changelog#{u['version']}",
            "published": u.get("released_at", ""),
            "author": u.get("developer_name", ""),
            "summary": u.get("release_notes", "New version released"),
        })
    return {
        "feed_title": "OpenSkill Marketplace Updates",
        "feed_link": f"{base_url}/marketplace/feed",
        "entries": entries, "entry_count": len(entries),
        "updated": entries[0]["published"] if entries else None,
    }


def build_atom_xml(*, feed: dict) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<feed xmlns="http://www.w3.org/2005/Atom">',
             f'  <title>{feed["feed_title"]}</title>',
             f'  <link href="{feed["feed_link"]}" rel="self"/>']
    if feed.get("updated"):
        lines.append(f'  <updated>{feed["updated"]}</updated>')
    for e in feed.get("entries", []):
        lines.extend([
            '  <entry>',
            f'    <title>{e["title"]}</title>',
            f'    <link href="{e["link"]}"/>',
            f'    <published>{e["published"]}</published>',
            f'    <summary>{e["summary"]}</summary>',
            '  </entry>',
        ])
    lines.append('</feed>')
    return '\n'.join(lines)
