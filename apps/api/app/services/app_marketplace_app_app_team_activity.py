"""Team activity — team member activity feed."""

import html
from datetime import datetime, timezone
from collections import defaultdict

ACTION_ICONS = {"deployed": "🚀", "reviewed": "⭐", "committed": "💻", "merged": "🔀",
                "commented": "💬", "created": "✨", "deleted": "🗑️", "updated": "🔄"}


def build_team_activity(*, activities: list[dict], limit: int = 20) -> dict:
    items = []
    by_member: dict[str, int] = defaultdict(int)
    for a in activities[:limit]:
        actor = html.escape(a.get("actor", ""))
        action = a.get("action", "updated")
        by_member[actor] += 1
        items.append({
            "actor": actor,
            "action": action,
            "icon": ACTION_ICONS.get(action, "📌"),
            "target": html.escape(a.get("target", "")),
            "timestamp": a.get("timestamp", datetime.now(timezone.utc).isoformat()),
        })
    top_contributors = sorted(by_member.items(), key=lambda x: -x[1])[:5]
    return {"activities": items, "total": len(items),
            "top_contributors": [{"name": n, "count": c} for n, c in top_contributors],
            "unique_members": len(by_member)}
