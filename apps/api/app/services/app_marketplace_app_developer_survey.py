"""Developer survey — collect feedback through structured surveys."""

from datetime import datetime, timezone


def create_survey(*, title: str, questions: list[dict]) -> dict:
    if not questions:
        return {"error": "At least one question required"}
    for q in questions:
        if q.get("type") not in ("text", "rating", "multiple_choice", "yes_no"):
            return {"error": f"Invalid question type: {q.get('type')}"}
    return {"title": title, "questions": questions, "status": "draft",
            "response_count": 0, "error": None}


def submit_response(*, survey_id: str, answers: list[dict]) -> dict:
    return {"survey_id": survey_id, "answers": answers,
            "submitted_at": datetime.now(timezone.utc).isoformat()}


def compute_survey_results(*, responses: list[dict], questions: list[dict]) -> dict:
    results = []
    for i, q in enumerate(questions):
        answers = [r["answers"][i] if i < len(r["answers"]) else None for r in responses]
        if q["type"] == "rating":
            values = [a.get("value", 0) for a in answers if a]
            avg = round(sum(values) / max(len(values), 1), 1)
            results.append({"question": q["text"], "type": "rating", "average": avg, "count": len(values)})
        else:
            results.append({"question": q["text"], "type": q["type"], "count": len([a for a in answers if a])})
    return {"results": results, "total_responses": len(responses)}
