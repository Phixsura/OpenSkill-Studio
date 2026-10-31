"""App API Developer Feedback Survey — structured developer surveys."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SurveyResponse:
    respondent: str
    answers: dict[str, str]

@dataclass
class Survey:
    survey_id: str
    title: str
    questions: list[str]
    responses: list[SurveyResponse] = field(default_factory=list)

    @property
    def response_count(self) -> int:
        return len(self.responses)

class AppAPIDeveloperFeedbackSurvey:
    def __init__(self) -> None:
        self._surveys: dict[tuple[str, str], Survey] = {}

    def create(self, installation_id: str, survey_id: str, title: str, questions: list[str]) -> Survey:
        if not installation_id: raise ValueError("installation_id is required")
        if not questions: raise ValueError("at least one question required")
        key = (installation_id, survey_id)
        if key in self._surveys: raise ValueError(f"Survey {survey_id} already exists")
        s = Survey(survey_id=survey_id, title=title, questions=questions)
        self._surveys[key] = s
        return s

    def submit_response(self, installation_id: str, survey_id: str, respondent: str, answers: dict[str, str]) -> Survey:
        s = self._get(installation_id, survey_id)
        s.responses.append(SurveyResponse(respondent=respondent, answers=answers))
        return s

    def get_survey(self, installation_id: str, survey_id: str) -> Survey:
        return self._get(installation_id, survey_id)

    def list_surveys(self, installation_id: str) -> list[Survey]:
        return [s for (inst, _), s in self._surveys.items() if inst == installation_id]

    def _get(self, installation_id: str, survey_id: str) -> Survey:
        s = self._surveys.get((installation_id, survey_id))
        if s is None: raise KeyError(f"Survey {survey_id} not found")
        return s
