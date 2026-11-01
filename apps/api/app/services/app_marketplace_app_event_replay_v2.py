"""Event replay v2 — selective replay with filtering and dry-run mode."""

from datetime import datetime, timezone


def create_replay_v2(*, app_id: str, event_filter: dict, target_url: str,
                        dry_run: bool = False) -> dict:
    return {"app_id": app_id, "filter": event_filter, "target_url": target_url,
            "dry_run": dry_run, "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat()}


def filter_events_for_replay(*, events: list[dict], filter_config: dict) -> list[dict]:
    result = events
    if filter_config.get("event_type"):
        result = [e for e in result if e.get("type") == filter_config["event_type"]]
    if filter_config.get("since"):
        result = [e for e in result if e.get("timestamp", "") >= filter_config["since"]]
    if filter_config.get("until"):
        result = [e for e in result if e.get("timestamp", "") <= filter_config["until"]]
    if filter_config.get("status"):
        result = [e for e in result if e.get("delivery_status") == filter_config["status"]]
    return result


def build_replay_preview(*, events: list[dict], dry_run: bool) -> dict:
    by_type = {}
    for e in events:
        t = e.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return {"event_count": len(events), "by_type": by_type,
            "dry_run": dry_run, "estimated_duration_s": len(events) * 0.1}
