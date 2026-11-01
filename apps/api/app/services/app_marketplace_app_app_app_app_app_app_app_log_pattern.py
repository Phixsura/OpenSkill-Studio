"""Log pattern detector — find recurring patterns in log data."""
from __future__ import annotations
import re
from collections import Counter


def detect_patterns(log_lines: list[str], min_count: int = 3) -> dict:
    # Normalize numbers and IDs to find patterns
    normalized = []
    for line in log_lines:
        norm = re.sub(r'\b\d+\b', '<NUM>', line)
        norm = re.sub(r'\b[0-9a-f]{8,}\b', '<ID>', norm, flags=re.IGNORECASE)
        normalized.append(norm)
    counts = Counter(normalized)
    patterns = [{"pattern": p, "count": c, "pct": round(c / len(log_lines) * 100, 1)}
                for p, c in counts.most_common() if c >= min_count]
    unique = len(counts)
    return {"patterns": patterns, "total_lines": len(log_lines),
            "unique_patterns": unique, "recurring_count": len(patterns),
            "compression_ratio": round(unique / max(len(log_lines), 1) * 100, 1)}
