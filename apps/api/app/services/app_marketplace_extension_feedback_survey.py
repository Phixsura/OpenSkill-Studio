"""Feedback Survey — collect developer and user feedback via surveys.

Creates surveys with multiple question types, collects responses,
aggregates results, and calculates NPS/CSAT scores.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SurveyQuestion:
    question_id: str
    text: str
    question_type: str  # rating, text, choice, nps
    choices: list[str] = field(default_factory=list)


@dataclass
class SurveyResponse:
    respondent_id: str
    answers: dict[str, str | int]  # question_id -> answer


class ExtensionFeedbackSurveyService:
    """Manages feedback surveys with NPS/CSAT scoring."""

    def __init__(self):
        self._surveys: dict[str, list[SurveyQuestion]] = {}
        self._responses: dict[str, list[SurveyResponse]] = defaultdict(list)

    def create_survey(self, survey_id: str, questions: list[dict]) -> list[SurveyQuestion]:
        parsed = [SurveyQuestion(
            question_id=f"q_{secrets.token_urlsafe(4)}",
            text=q["text"], question_type=q.get("type", "text"),
            choices=q.get("choices", []),
        ) for q in questions]
        self._surveys[survey_id] = parsed
        return parsed

    def submit_response(self, survey_id: str, respondent_id: str,
                        answers: dict[str, str | int]) -> bool:
        if survey_id not in self._surveys:
            return False
        # Prevent duplicate
        if any(r.respondent_id == respondent_id for r in self._responses[survey_id]):
            return False
        self._responses[survey_id].append(
            SurveyResponse(respondent_id=respondent_id, answers=answers))
        return True

    def get_results(self, survey_id: str) -> dict:
        responses = self._responses.get(survey_id, [])
        questions = self._surveys.get(survey_id, [])
        results: dict[str, dict] = {}
        for q in questions:
            answers = [r.answers.get(q.question_id) for r in responses if q.question_id in r.answers]
            if q.question_type == "rating" or q.question_type == "nps":
                numeric = [a for a in answers if isinstance(a, (int, float))]
                results[q.question_id] = {
                    "text": q.text, "type": q.question_type,
                    "count": len(numeric),
                    "average": round(sum(numeric) / max(len(numeric), 1), 1),
                }
            elif q.question_type == "choice":
                counts: dict[str, int] = defaultdict(int)
                for a in answers:
                    counts[str(a)] += 1
                results[q.question_id] = {"text": q.text, "type": "choice", "counts": dict(counts)}
            else:
                results[q.question_id] = {"text": q.text, "type": "text", "count": len(answers)}
        return {"survey_id": survey_id, "responses": len(responses), "questions": results}

    def calculate_nps(self, survey_id: str, nps_question_id: str) -> dict:
        responses = self._responses.get(survey_id, [])
        scores = [r.answers.get(nps_question_id) for r in responses
                  if isinstance(r.answers.get(nps_question_id), (int, float))]
        if not scores:
            return {"nps": 0, "responses": 0}
        promoters = sum(1 for s in scores if s >= 9) / len(scores) * 100
        detractors = sum(1 for s in scores if s <= 6) / len(scores) * 100
        return {"nps": round(promoters - detractors, 1), "responses": len(scores),
                "promoters_pct": round(promoters, 1), "detractors_pct": round(detractors, 1)}
