"""Feedback survey — post-install and post-uninstall feedback collection."""


def build_install_survey(*, app_name: str) -> dict:
    return {"title": f"Welcome to {app_name}!", "type": "post_install",
            "questions": [
                {"id": "q1", "text": "How did you hear about this app?", "type": "select",
                 "options": ["Marketplace search", "Recommendation", "Social media", "Blog post", "Other"]},
                {"id": "q2", "text": "What's your primary use case?", "type": "text"},
                {"id": "q3", "text": "How easy was the installation?", "type": "rating", "max": 5},
            ]}


def build_uninstall_survey(*, app_name: str) -> dict:
    return {"title": f"Help us improve {app_name}", "type": "post_uninstall",
            "questions": [
                {"id": "q1", "text": "Why are you uninstalling?", "type": "select",
                 "options": ["Not needed anymore", "Too expensive", "Missing features", "Too complex", "Found alternative", "Other"]},
                {"id": "q2", "text": "Any additional feedback?", "type": "text"},
                {"id": "q3", "text": "Would you consider using it again?", "type": "select", "options": ["Yes", "Maybe", "No"]},
            ]}


def analyze_survey_responses(*, responses: list[dict]) -> dict:
    if not responses:
        return {"total": 0, "avg_rating": 0, "top_reasons": []}
    ratings = [r.get("rating", 0) for r in responses if r.get("rating")]
    from collections import Counter
    reasons = Counter(r.get("reason", "") for r in responses if r.get("reason"))
    return {"total": len(responses), "avg_rating": round(sum(ratings) / max(len(ratings), 1), 1),
            "top_reasons": [{"reason": r, "count": c} for r, c in reasons.most_common(5)]}
