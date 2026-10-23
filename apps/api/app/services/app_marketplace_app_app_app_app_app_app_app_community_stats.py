"""Developer community stats — community engagement metrics."""
from __future__ import annotations


def compute_community_stats(*, forum_posts: int, forum_replies: int,
                               github_stars: int, github_forks: int,
                               discord_members: int, twitter_followers: int,
                               blog_posts: int, community_apps: int) -> dict:
    engagement = forum_posts + forum_replies
    open_source_health = round((github_stars + github_forks * 2) / max(community_apps, 1), 1)
    return {
        "forum": {"posts": forum_posts, "replies": forum_replies,
                   "engagement": engagement, "display": f"{engagement:,}"},
        "github": {"stars": github_stars, "forks": github_forks,
                    "stars_display": f"{github_stars:,}", "forks_display": f"{github_forks:,}"},
        "social": {"discord": discord_members, "twitter": twitter_followers,
                    "discord_display": f"{discord_members:,}",
                    "twitter_display": f"{twitter_followers:,}"},
        "content": {"blog_posts": blog_posts, "community_apps": community_apps},
        "open_source_health": open_source_health,
        "community_score": _score(engagement, github_stars, discord_members),
    }


def _score(engagement: int, stars: int, discord: int) -> str:
    total = engagement + stars + discord
    if total > 10000:
        return "vibrant"
    if total > 1000:
        return "active"
    return "growing"
