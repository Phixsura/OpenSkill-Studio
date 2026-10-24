"""Request sampling engine — intelligent request sampling for observability."""
from __future__ import annotations
import hashlib


def should_sample(request_id: str, sample_rate: float, priority: str = "normal") -> dict:
    if priority == "high":
        return {"sampled": True, "reason": "high_priority"}
    if priority == "error":
        return {"sampled": True, "reason": "error_always_sampled"}
    h = int(hashlib.md5(request_id.encode()).hexdigest(), 16) % 10000
    threshold = int(sample_rate * 10000)
    sampled = h < threshold
    return {"sampled": sampled, "reason": "rate_based", "rate": sample_rate}


def sampling_stats(total: int, sampled: int, target_rate: float) -> dict:
    actual_rate = round(sampled / max(total, 1), 4)
    deviation = round(abs(actual_rate - target_rate) / max(target_rate, 0.0001) * 100, 1)
    return {"total": total, "sampled": sampled, "dropped": total - sampled,
            "target_rate": target_rate, "actual_rate": actual_rate,
            "deviation_pct": deviation, "accurate": deviation < 5}
