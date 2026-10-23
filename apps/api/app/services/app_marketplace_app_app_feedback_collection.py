"""Feedback collection — in-app feedback survey builder."""

import html
import secrets
from datetime import datetime, timezone

QUESTION_TYPES = {"rating", "text", "multiple_choice", "nps"}


def build_survey(*, title: str, questions: list[dict]) -> dict:
    items = []
    for q in questions:
        qtype = q.get("type", "text")
        if qtype not in QUESTION_TYPES:
            continue
        items.append({
            "id": f"q_{secrets.token_hex(3)}",
            "text": html.escape(q.get("text", "")),
            "type": qtype,
            "required": q.get("required", False),
            "options": q.get("options"),
        })
    return {"title": html.escape(title), "questions": items,
            "question_count": len(items),
            "estimated_time_min": max(1, len(items) // 3)}


def submit_survey(*, survey_id: str, answers: dict[str, str | int]) -> dict:
    return {"submission_id": f"sub_{secrets.token_hex(6)}",
            "survey_id": survey_id, "answer_count": len(answers),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "message": "Thank you for your feedback! 🙏"}
