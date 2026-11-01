"""Error tracker — real-time error tracking and grouping."""

import html
import hashlib
from collections import defaultdict
from datetime import datetime, timezone


def track_error(*, message: str, stack: str = "", source: str = "",
                  user_id: str = "", url: str = "") -> dict:
    fingerprint = hashlib.sha256(f"{message}:{source}".encode()).hexdigest()[:12]
    return {
        "fingerprint": fingerprint,
        "message": html.escape(message),
        "stack": html.escape(stack[:500]),
        "source": html.escape(source),
        "user_id": user_id, "url": html.escape(url),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def group_errors(*, errors: list[dict]) -> dict:
    groups: dict[str, list] = defaultdict(list)
    for e in errors:
        groups[e.get("fingerprint", "")].append(e)
    items = [{"fingerprint": fp, "message": errs[0].get("message", ""),
              "count": len(errs), "first_seen": errs[0].get("timestamp", ""),
              "last_seen": errs[-1].get("timestamp", ""),
              "affected_users": len(set(e.get("user_id", "") for e in errs if e.get("user_id")))}
             for fp, errs in groups.items()]
    items.sort(key=lambda x: -x["count"])
    return {"groups": items, "total_errors": len(errors),
            "unique_errors": len(items),
            "top_error": items[0]["message"] if items else None}
