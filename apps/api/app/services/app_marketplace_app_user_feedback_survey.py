"""User feedback survey — collect NPS and satisfaction data."""

import secrets


def create_survey(*, app_id: str, survey_type: str = "nps",
                    questions: list[dict] | None = None) -> dict:
    valid_types = {"nps", "csat", "ces", "custom"}
    if survey_type not in valid_types:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(valid_types))}"}
    default_q = {
        "nps": [{"id": "q1", "text": "How likely are you to recommend this app?", "type": "scale", "min": 0, "max": 10}],
        "csat": [{"id": "q1", "text": "How satisfied are you?", "type": "scale", "min": 1, "max": 5}],
        "ces": [{"id": "q1", "text": "How easy was it to use?", "type": "scale", "min": 1, "max": 7}],
        "custom": questions or [],
    }
    return {
        "survey_id": f"srv_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "type": survey_type,
        "questions": default_q[survey_type],
        "status": "active",
    }


def calculate_nps(*, responses: list[int]) -> dict:
    if not responses:
        return {"error": "No responses"}
    promoters = sum(1 for r in responses if r >= 9)
    detractors = sum(1 for r in responses if r <= 6)
    total = len(responses)
    nps = round((promoters - detractors) / total * 100, 1)
    return {
        "nps_score": nps,
        "promoters": promoters,
        "passives": total - promoters - detractors,
        "detractors": detractors,
        "total_responses": total,
        "category": "excellent" if nps >= 50 else "good" if nps >= 0 else "needs_improvement",
    }
