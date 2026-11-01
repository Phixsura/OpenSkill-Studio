"""Developer Score — composite scoring system for marketplace developers.

Calculates a single developer score from multiple weighted dimensions:
code quality, community engagement, responsiveness, and reliability.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ScoreDimension:
    name: str
    value: float  # 0-100
    weight: float  # 0-1
    description: str = ""


class DeveloperScoreService:
    """Calculates composite developer scores."""

    DIMENSIONS = {
        "code_quality": {"weight": 0.25, "description": "Test coverage, lint pass rate, security scan results"},
        "community": {"weight": 0.20, "description": "Reviews responded to, contributions, forum activity"},
        "responsiveness": {"weight": 0.20, "description": "Support response time, issue resolution speed"},
        "reliability": {"weight": 0.20, "description": "Uptime, crash-free rate, SLA compliance"},
        "adoption": {"weight": 0.15, "description": "Downloads, active installs, growth rate"},
    }

    def __init__(self):
        self._scores: dict[str, dict[str, float]] = {}

    def set_dimension(self, developer_id: str, dimension: str, value: float) -> bool:
        if dimension not in self.DIMENSIONS:
            return False
        self._scores.setdefault(developer_id, {})[dimension] = max(0, min(100, value))
        return True

    def set_all_dimensions(self, developer_id: str, values: dict[str, float]) -> None:
        for dim, val in values.items():
            self.set_dimension(developer_id, dim, val)

    def calculate_score(self, developer_id: str) -> float:
        dims = self._scores.get(developer_id, {})
        if not dims:
            return 0.0
        total = 0.0
        total_weight = 0.0
        for dim_name, config in self.DIMENSIONS.items():
            if dim_name in dims:
                total += dims[dim_name] * config["weight"]
                total_weight += config["weight"]
        if total_weight == 0:
            return 0.0
        return round(total / total_weight * (total_weight / sum(c["weight"] for c in self.DIMENSIONS.values())), 1)

    def get_breakdown(self, developer_id: str) -> list[ScoreDimension]:
        dims = self._scores.get(developer_id, {})
        return [
            ScoreDimension(name, dims.get(name, 0), cfg["weight"], cfg["description"])
            for name, cfg in self.DIMENSIONS.items()
        ]

    def get_grade(self, score: float) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B"
        if score >= 60: return "C"
        if score >= 50: return "D"
        return "F"

    def get_improvement_tips(self, developer_id: str) -> list[dict]:
        dims = self._scores.get(developer_id, {})
        tips = []
        for dim_name, cfg in self.DIMENSIONS.items():
            val = dims.get(dim_name, 0)
            if val < 70:
                tips.append({
                    "dimension": dim_name,
                    "current": val,
                    "target": 80,
                    "impact": cfg["weight"],
                    "tip": f"Improve {dim_name.replace('_', ' ')}: {cfg['description']}",
                })
        return sorted(tips, key=lambda t: t["impact"], reverse=True)

    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        results = []
        for dev_id in self._scores:
            score = self.calculate_score(dev_id)
            results.append({"developer_id": dev_id, "score": score, "grade": self.get_grade(score)})
        return sorted(results, key=lambda r: r["score"], reverse=True)[:limit]
