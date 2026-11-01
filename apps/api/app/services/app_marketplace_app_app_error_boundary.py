"""Error boundary — structured error capture and reporting."""

import html
import traceback
import hashlib
from datetime import datetime, timezone


def capture_error(*, error: Exception | str, context: dict | None = None) -> dict:
    if isinstance(error, Exception):
        msg = str(error)
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        stack = "".join(tb)
        error_type = type(error).__name__
    else:
        msg = str(error)
        stack = ""
        error_type = "Error"
    fingerprint = hashlib.sha256(f"{error_type}:{msg}".encode()).hexdigest()[:12]
    return {
        "id": fingerprint,
        "type": error_type,
        "message": html.escape(msg),
        "stack": html.escape(stack) if stack else None,
        "context": context or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": "error",
    }


def build_error_summary(*, errors: list[dict]) -> dict:
    grouped: dict[str, list] = {}
    for e in errors:
        grouped.setdefault(e["id"], []).append(e)
    groups = [{"fingerprint": k, "count": len(v), "type": v[0]["type"],
               "message": v[0]["message"], "last_seen": v[-1]["timestamp"]}
              for k, v in grouped.items()]
    groups.sort(key=lambda x: x["count"], reverse=True)
    return {"groups": groups, "total_errors": len(errors),
            "unique_errors": len(groups)}
