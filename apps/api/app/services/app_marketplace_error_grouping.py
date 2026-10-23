"""Error grouping — group similar errors by fingerprint for efficient triage."""

import hashlib
from collections import defaultdict


def compute_error_fingerprint(*, error_type: str, message: str, stack_trace: str = "") -> str:
    # Normalize: strip line numbers and memory addresses
    import re
    normalized_stack = re.sub(r':\d+:\d+', ':X:X', stack_trace)
    normalized_stack = re.sub(r'0x[0-9a-f]+', '0xXXXX', normalized_stack)
    content = f"{error_type}:{message}:{normalized_stack}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def group_errors(*, errors: list[dict]) -> list[dict]:
    groups: dict[str, dict] = {}
    for e in errors:
        fp = compute_error_fingerprint(error_type=e.get("type", ""), message=e.get("message", ""),
                                        stack_trace=e.get("stack_trace", ""))
        if fp not in groups:
            groups[fp] = {"fingerprint": fp, "type": e.get("type"), "message": e.get("message"),
                           "count": 0, "first_seen": e.get("timestamp"), "last_seen": e.get("timestamp"),
                           "events": []}
        groups[fp]["count"] += 1
        groups[fp]["last_seen"] = e.get("timestamp", groups[fp]["last_seen"])
        groups[fp]["events"].append(e)
    return sorted(groups.values(), key=lambda g: -g["count"])


def prioritize_error_groups(*, groups: list[dict]) -> list[dict]:
    for g in groups:
        score = g["count"] * 10
        if g.get("type") in ("TypeError", "NullPointerException", "FATAL"):
            score *= 2
        g["priority_score"] = score
    return sorted(groups, key=lambda g: -g["priority_score"])
