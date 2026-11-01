"""Community page — developer community hub with discussions and resources."""

import html
from datetime import datetime, timezone

COMMUNITY_LINKS = [
    {"id": "discord", "name": "Discord", "icon": "💬", "href": "https://discord.gg/openskill", "members": 5200},
    {"id": "github", "name": "GitHub Discussions", "icon": "🐙", "href": "https://github.com/openskill/discussions", "members": 3800},
    {"id": "forum", "name": "Community Forum", "icon": "📝", "href": "https://forum.openskill.dev", "members": 2100},
    {"id": "twitter", "name": "Twitter/X", "icon": "🐦", "href": "https://twitter.com/openskill", "members": 8500},
]


def build_community_page(*, recent_discussions: list[dict] | None = None,
                            top_contributors: list[dict] | None = None) -> dict:
    discussions = [{"title": html.escape(d.get("title", "")), "author": html.escape(d.get("author", "")),
                     "replies": d.get("replies", 0), "date": d.get("date", "")}
                    for d in (recent_discussions or [])[:5]]
    contributors = [{"name": html.escape(c.get("name", "")), "contributions": c.get("contributions", 0),
                      "badge": c.get("badge", "🌟")} for c in (top_contributors or [])[:5]]
    total_members = sum(l["members"] for l in COMMUNITY_LINKS)
    return {"links": COMMUNITY_LINKS, "discussions": discussions,
            "contributors": contributors, "total_members": total_members,
            "link_count": len(COMMUNITY_LINKS)}
