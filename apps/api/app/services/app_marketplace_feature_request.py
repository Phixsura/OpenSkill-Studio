"""Feature request — user-submitted feature requests with voting."""

from datetime import datetime, timezone


def create_feature_request(*, app_id: str, user_id: str, title: str, description: str) -> dict:
    if len(title) < 5:
        return {"error": "Title too short (min 5 chars)"}
    return {
        "app_id": app_id, "user_id": user_id, "title": title, "description": description,
        "status": "open", "votes": 1, "voters": [user_id],
        "created_at": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def vote(*, request: dict, user_id: str) -> dict:
    voters = list(request.get("voters", []))
    if user_id in voters:
        return {"error": "Already voted", "votes": request.get("votes", 0)}
    voters.append(user_id)
    return {"votes": len(voters), "voters": voters, "error": None}


def rank_requests(*, requests: list[dict]) -> list[dict]:
    return sorted(requests, key=lambda r: (-r.get("votes", 0), r.get("created_at", "")))
