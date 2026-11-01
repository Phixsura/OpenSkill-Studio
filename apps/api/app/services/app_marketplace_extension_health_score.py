"""Extension Health Score — composite health metric for extensions."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class HealthMetrics:
    uptime_pct: float = 100.0
    error_rate_pct: float = 0.0
    avg_response_ms: float = 50.0
    update_frequency_days: int = 7
    open_issues: int = 0
    test_coverage_pct: float = 80.0
    security_score: float = 100.0


class ExtHealthScoreService:
    WEIGHTS = {
        "uptime": 25, "error_rate": 20, "response_time": 15,
        "update_freq": 10, "issues": 10, "coverage": 10, "security": 10,
    }

    def calculate(self, metrics: HealthMetrics) -> dict:
        scores = {}
        # Uptime: 100% = 100, below 99% drops fast
        scores["uptime"] = min(100, metrics.uptime_pct * 1.01)
        # Error rate: 0% = 100, each 1% costs 20 points
        scores["error_rate"] = max(0, 100 - metrics.error_rate_pct * 20)
        # Response time: <100ms = 100, degrades linearly to 1000ms
        scores["response_time"] = max(0, min(100, 100 - (metrics.avg_response_ms - 100) / 9))
        # Update frequency: weekly = 100, monthly = 50, stale = 0
        if metrics.update_frequency_days <= 7: scores["update_freq"] = 100
        elif metrics.update_frequency_days <= 30: scores["update_freq"] = 50
        elif metrics.update_frequency_days <= 90: scores["update_freq"] = 25
        else: scores["update_freq"] = 0
        # Open issues
        scores["issues"] = max(0, 100 - metrics.open_issues * 5)
        # Test coverage
        scores["coverage"] = min(100, metrics.test_coverage_pct)
        # Security
        scores["security"] = min(100, metrics.security_score)

        weighted = sum(scores[k] * self.WEIGHTS[k] / 100 for k in self.WEIGHTS)
        grade = "A" if weighted >= 90 else "B" if weighted >= 75 else "C" if weighted >= 60 else "D" if weighted >= 40 else "F"

        return {"score": round(weighted, 1), "grade": grade,
                "breakdown": {k: round(v, 1) for k, v in scores.items()}}

    def compare(self, a: HealthMetrics, b: HealthMetrics) -> dict:
        score_a = self.calculate(a)
        score_b = self.calculate(b)
        return {"a": score_a["score"], "b": score_b["score"],
                "winner": "a" if score_a["score"] > score_b["score"] else "b",
                "diff": round(abs(score_a["score"] - score_b["score"]), 1)}
