"""Developer roadmap — public roadmap of upcoming platform features."""

ROADMAP = {
    "in_progress": [
        {"id": "r1", "title": "GraphQL API", "description": "Native GraphQL endpoint for all resources", "eta": "Q4 2026"},
        {"id": "r2", "title": "Mobile SDK", "description": "React Native and Flutter SDKs", "eta": "Q4 2026"},
    ],
    "planned": [
        {"id": "r3", "title": "AI Recommendations", "description": "ML-powered app recommendations", "eta": "Q1 2027"},
        {"id": "r4", "title": "Marketplace Analytics v4", "description": "Predictive analytics and forecasting", "eta": "Q1 2027"},
        {"id": "r5", "title": "Multi-language Support", "description": "15+ languages for marketplace UI", "eta": "Q2 2027"},
    ],
    "completed": [
        {"id": "r0", "title": "100K Lines Milestone", "description": "Complete developer platform shipped", "completed_at": "2026-10"},
    ],
}


def get_roadmap() -> dict:
    total = sum(len(items) for items in ROADMAP.values())
    return {"categories": ROADMAP, "total_items": total,
            "in_progress_count": len(ROADMAP["in_progress"]),
            "planned_count": len(ROADMAP["planned"]),
            "completed_count": len(ROADMAP["completed"])}


def vote_on_feature(*, feature_id: str, user_id: str, votes: dict[str, int]) -> dict:
    current = votes.get(feature_id, 0)
    votes[feature_id] = current + 1
    return {"feature_id": feature_id, "votes": votes[feature_id], "voted": True}
