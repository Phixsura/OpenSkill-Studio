"""Consumer API Endpoint Health Score — composite health scoring per endpoint."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

WEIGHTS = {"availability": 0.3, "latency": 0.25, "error_rate": 0.25, "throughput": 0.2}


@dataclass
class HealthInput:
    endpoint_id: str
    availability_pct: float = 100.0
    latency_p95_ms: float = 0.0
    latency_target_ms: float = 200.0
    error_rate_pct: float = 0.0
    throughput_rps: float = 0.0
    throughput_target_rps: float = 100.0


@dataclass
class EndpointHealthScorer:
    """Compute composite health scores for API endpoints."""

    _scores: dict[str, dict] = field(default_factory=dict)

    def score(self, inp: HealthInput) -> dict:
        # Availability score (0-100)
        avail_score = min(100, inp.availability_pct)
        # Latency score (lower is better)
        if inp.latency_target_ms > 0:
            lat_ratio = inp.latency_p95_ms / inp.latency_target_ms
            lat_score = max(0, min(100, (2 - lat_ratio) * 50))
        else:
            lat_score = 100.0
        # Error rate score (lower is better)
        err_score = max(0, 100 - inp.error_rate_pct * 10)
        # Throughput score
        if inp.throughput_target_rps > 0:
            thr_ratio = inp.throughput_rps / inp.throughput_target_rps
            thr_score = min(100, thr_ratio * 100)
        else:
            thr_score = 100.0

        composite = (
            avail_score * WEIGHTS["availability"] +
            lat_score * WEIGHTS["latency"] +
            err_score * WEIGHTS["error_rate"] +
            thr_score * WEIGHTS["throughput"]
        )
        composite = round(composite, 1)

        if composite >= 90:
            grade = "A"
        elif composite >= 75:
            grade = "B"
        elif composite >= 60:
            grade = "C"
        elif composite >= 40:
            grade = "D"
        else:
            grade = "F"

        result = {
            "endpoint_id": inp.endpoint_id,
            "composite_score": composite,
            "grade": grade,
            "components": {
                "availability": round(avail_score, 1),
                "latency": round(lat_score, 1),
                "error_rate": round(err_score, 1),
                "throughput": round(thr_score, 1),
            },
        }
        self._scores[inp.endpoint_id] = result
        logger.info("health_score_computed", endpoint=inp.endpoint_id, score=composite)
        return result

    def get_score(self, endpoint_id: str) -> dict | None:
        return self._scores.get(endpoint_id)

    def get_ranking(self, limit: int = 20) -> list[dict]:
        ranked = sorted(self._scores.values(), key=lambda x: x["composite_score"], reverse=True)
        for i, r in enumerate(ranked):
            r["rank"] = i + 1
        return ranked[:limit]

    def get_summary(self) -> dict:
        if not self._scores:
            return {"total": 0}
        scores = [s["composite_score"] for s in self._scores.values()]
        grades = {}
        for s in self._scores.values():
            grades[s["grade"]] = grades.get(s["grade"], 0) + 1
        return {
            "total": len(scores),
            "avg_score": round(sum(scores) / len(scores), 1),
            "min_score": min(scores),
            "max_score": max(scores),
            "by_grade": grades,
        }
