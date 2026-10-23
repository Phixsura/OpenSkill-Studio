"""Onboarding quiz — assess developer skill level to personalize experience."""

QUESTIONS = [
    {"id": "q1", "text": "How familiar are you with REST APIs?", "options": ["Beginner", "Intermediate", "Expert"]},
    {"id": "q2", "text": "Have you built webhooks before?", "options": ["No", "A few times", "Regularly"]},
    {"id": "q3", "text": "Which languages do you primarily use?", "options": ["JavaScript/TypeScript", "Python", "Go", "Other"]},
    {"id": "q4", "text": "What's your main goal?", "options": ["Build an internal tool", "Publish to marketplace", "Integrate services"]},
]


def get_quiz() -> list[dict]:
    return QUESTIONS


def evaluate_quiz(*, answers: dict[str, str]) -> dict:
    score = 0
    expert_answers = {"q1": "Expert", "q2": "Regularly"}
    for qid, ans in answers.items():
        if qid in expert_answers and ans == expert_answers[qid]:
            score += 2
        elif ans in ("Intermediate", "A few times"):
            score += 1
    level = "expert" if score >= 4 else "intermediate" if score >= 2 else "beginner"
    recommended_track = {
        "beginner": "guided_tutorial",
        "intermediate": "quickstart",
        "expert": "api_reference",
    }
    return {"level": level, "score": score, "recommended_track": recommended_track[level],
            "skip_basics": level != "beginner"}
