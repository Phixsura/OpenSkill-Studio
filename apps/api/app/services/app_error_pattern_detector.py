"""Error pattern detector — detect recurring error patterns."""

from collections import Counter


def detect_patterns(errors: list[dict], *, min_occurrences: int = 3) -> list[dict]:
    """Detect recurring error patterns."""
    type_counts = Counter(e.get("error_type", "unknown") for e in errors)
    message_counts = Counter(e.get("message", "")[:100] for e in errors)
    
    patterns = []
    for error_type, count in type_counts.most_common():
        if count >= min_occurrences:
            patterns.append({"type": error_type, "count": count, "frequency": "recurring"})
    
    return patterns


def is_new_error(error_type: str, known_patterns: list[dict]) -> bool:
    return not any(p["type"] == error_type for p in known_patterns)
