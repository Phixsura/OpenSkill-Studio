"""Developer community page — forums, discussions, and Q&A."""


def build_community_page(*, discussions: list[dict], popular_tags: list[dict],
                             members_count: int, online_count: int) -> dict:
    pinned = [d for d in discussions if d.get("pinned")]
    recent = [d for d in discussions if not d.get("pinned")][:20]
    return {
        "page_type": "community",
        "stats": {"members": members_count, "online": online_count,
                   "discussions": len(discussions)},
        "pinned": pinned,
        "recent": recent,
        "popular_tags": popular_tags[:10],
        "categories": ["general", "help", "showcase", "feedback", "announcements"],
        "cta": {"label": "Start a Discussion", "url": "/community/new"},
    }


def build_discussion_detail(*, discussion: dict, replies: list[dict]) -> dict:
    return {
        "discussion": discussion,
        "replies": replies,
        "reply_count": len(replies),
        "can_reply": True,
        "related": [],
    }
