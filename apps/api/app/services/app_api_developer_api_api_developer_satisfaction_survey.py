"""App API Developer Satisfaction Survey — NPS and satisfaction tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SurveyResponse:
    response_id: str
    developer_id: str
    nps_score: int  # 0-10
    satisfaction: int  # 1-5
    comment: str = ""

class AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey:
    def __init__(self) -> None:
        self._responses: dict[tuple[str, str], SurveyResponse] = {}

    def submit(self, installation_id: str, response_id: str, developer_id: str, nps_score: int, satisfaction: int, comment: str = "") -> SurveyResponse:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= nps_score <= 10: raise ValueError("nps_score must be 0-10")
        if not 1 <= satisfaction <= 5: raise ValueError("satisfaction must be 1-5")
        key = (installation_id, response_id)
        if key in self._responses: raise ValueError(f"Response {response_id} exists")
        r = SurveyResponse(response_id=response_id, developer_id=developer_id, nps_score=nps_score, satisfaction=satisfaction, comment=comment)
        self._responses[key] = r
        return r

    def nps(self, installation_id: str) -> float:
        responses = [r for (inst, _), r in self._responses.items() if inst == installation_id]
        if not responses: return 0.0
        promoters = sum(1 for r in responses if r.nps_score >= 9)
        detractors = sum(1 for r in responses if r.nps_score <= 6)
        return round((promoters - detractors) / len(responses) * 100, 1)

    def avg_satisfaction(self, installation_id: str) -> float:
        responses = [r for (inst, _), r in self._responses.items() if inst == installation_id]
        if not responses: return 0.0
        return round(sum(r.satisfaction for r in responses) / len(responses), 1)

    def response_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._responses if inst == installation_id)

    def recent_comments(self, installation_id: str, limit: int = 10) -> list[str]:
        responses = [r for (inst, _), r in self._responses.items() if inst == installation_id and r.comment]
        return [r.comment for r in responses[-limit:]]
