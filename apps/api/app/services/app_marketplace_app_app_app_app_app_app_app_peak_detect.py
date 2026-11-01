"""Traffic peak detector — detect traffic peaks and predict capacity needs."""
from __future__ import annotations
import math


def detect_peaks(hourly_traffic: list[dict]) -> dict:
    if not hourly_traffic:
        return {"peaks": [], "avg_rps": 0}
    rps_values = [h.get("rps", 0) for h in hourly_traffic]
    avg = sum(rps_values) / len(rps_values)
    std = math.sqrt(sum((x - avg) ** 2 for x in rps_values) / len(rps_values)) if len(rps_values) > 1 else 0
    threshold = avg + 2 * std
    peaks = []
    for h in hourly_traffic:
        if h["rps"] > threshold:
            peaks.append({"hour": h["hour"], "rps": h["rps"],
                          "above_avg_pct": round((h["rps"] - avg) / max(avg, 0.01) * 100, 1)})
    return {"peaks": peaks, "avg_rps": round(avg, 1), "peak_threshold": round(threshold, 1),
            "max_rps": max(rps_values), "total_hours": len(hourly_traffic)}
