"""Event replay manager — replay historical events for debugging and testing."""

from datetime import datetime, timezone


def create_replay_job(*, app_id: str, event_ids: list[str], target_url: str) -> dict:
    if not event_ids:
        return {"error": "No events to replay"}
    if len(event_ids) > 100:
        return {"error": "Maximum 100 events per replay"}
    return {"app_id": app_id, "event_count": len(event_ids), "target_url": target_url,
            "status": "queued", "created_at": datetime.now(timezone.utc).isoformat(), "error": None}


def execute_replay(*, events: list[dict]) -> dict:
    results = []
    for e in events:
        results.append({"event_id": e.get("id"), "status": "delivered", "status_code": 200})
    delivered = sum(1 for r in results if r["status"] == "delivered")
    return {"total": len(events), "delivered": delivered, "failed": len(events) - delivered, "results": results}


def build_replay_summary(*, job: dict, results: dict) -> dict:
    return {"app_id": job["app_id"], "events_replayed": results["total"],
            "success_rate": round(results["delivered"] / max(results["total"], 1) * 100, 1),
            "completed_at": datetime.now(timezone.utc).isoformat()}
