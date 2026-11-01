"""Token usage meter — track API token consumption."""
from __future__ import annotations
import time

_usage: dict[str, dict] = {}


def record_usage(token_id: str, endpoint: str, tokens_consumed: int = 1) -> dict:
    if token_id not in _usage:
        _usage[token_id] = {"token_id": token_id, "total": 0, "by_endpoint": {},
                             "first_used": time.time(), "last_used": 0}
    entry = _usage[token_id]
    entry["total"] += tokens_consumed
    entry["by_endpoint"][endpoint] = entry["by_endpoint"].get(endpoint, 0) + tokens_consumed
    entry["last_used"] = time.time()
    return {"recorded": True, "total": entry["total"]}


def get_usage(token_id: str) -> dict:
    entry = _usage.get(token_id)
    if not entry:
        return {"found": False}
    top = max(entry["by_endpoint"], key=entry["by_endpoint"].get) if entry["by_endpoint"] else None
    return {"found": True, **entry, "top_endpoint": top,
            "endpoint_count": len(entry["by_endpoint"])}


def usage_summary() -> dict:
    total_tokens = sum(e["total"] for e in _usage.values())
    active_keys = len(_usage)
    return {"total_consumed": total_tokens, "active_keys": active_keys,
            "avg_per_key": round(total_tokens / max(active_keys, 1))}


def clear_usage() -> None:
    _usage.clear()
