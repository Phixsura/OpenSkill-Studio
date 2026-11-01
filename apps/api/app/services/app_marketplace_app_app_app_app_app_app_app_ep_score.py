"""API endpoint health score — composite health per endpoint."""
from __future__ import annotations


def score_endpoint(metrics: dict) -> dict:
    avail = min(100, metrics.get("availability_pct", 100))
    latency_score = max(0, 100 - metrics.get("p99_ms", 0) / 10)
    error_score = max(0, 100 - metrics.get("error_rate_pct", 0) * 20)
    throughput_ok = 100 if metrics.get("rps", 0) > 0 else 50
    composite = round(avail * 0.35 + latency_score * 0.25 + error_score * 0.25 + throughput_ok * 0.15, 1)
    grade = "A" if composite >= 90 else ("B" if composite >= 75 else ("C" if composite >= 60 else "F"))
    return {"endpoint": metrics.get("endpoint", ""), "score": composite, "grade": grade,
            "breakdown": {"availability": round(avail, 1), "latency": round(latency_score, 1),
                          "errors": round(error_score, 1), "throughput": throughput_ok}}


def rank_endpoints(endpoints: list[dict]) -> list[dict]:
    scored = [score_endpoint(e) for e in endpoints]
    return sorted(scored, key=lambda s: s["score"])
