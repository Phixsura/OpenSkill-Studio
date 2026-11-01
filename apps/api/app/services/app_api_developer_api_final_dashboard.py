"""App API Developer Final Dashboard — THE complete developer platform dashboard.

The ultimate service — aggregates everything into one final dashboard view:
- Platform health grade
- API performance grade
- Webhook delivery grade
- Developer experience grade
- Overall platform score
"""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class FinalDashboard:
    platform_health_grade: str = "A"
    api_performance_grade: str = "A"
    webhook_delivery_grade: str = "A"
    developer_experience_grade: str = "A"
    documentation_grade: str = "A"
    security_grade: str = "A"
    total_developers: int = 0
    total_api_calls: int = 0
    overall_uptime: float = 100.0
    nps_score: float = 0.0

    @property
    def overall_grade(self) -> str:
        grades = {"A+": 4.3, "A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0}
        values = [
            grades.get(self.platform_health_grade, 2.0),
            grades.get(self.api_performance_grade, 2.0),
            grades.get(self.webhook_delivery_grade, 2.0),
            grades.get(self.developer_experience_grade, 2.0),
            grades.get(self.documentation_grade, 2.0),
            grades.get(self.security_grade, 2.0),
        ]
        avg = sum(values) / len(values)
        if avg >= 4.0: return "A"
        if avg >= 3.0: return "B"
        if avg >= 2.0: return "C"
        return "D"

class AppAPIDeveloperAPIFinalDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, FinalDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> FinalDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = FinalDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> FinalDashboard:
        return self._dashboards.get(installation_id, FinalDashboard())
