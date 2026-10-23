"""Review form — structured review submission with validation."""

import re

PROFANITY_CHECK = {"spam", "scam", "fake", "sucks"}


def validate_review(*, rating: int, title: str, body: str, pros: list[str],
                       cons: list[str]) -> dict:
    errors = []
    if rating < 1 or rating > 5:
        errors.append("Rating must be 1-5")
    if len(title) < 5 or len(title) > 100:
        errors.append("Title must be 5-100 characters")
    if len(body) < 20:
        errors.append("Review must be at least 20 characters")
    if len(body) > 5000:
        errors.append("Review must be under 5000 characters")
    combined = f"{title} {body}".lower()
    flagged = [w for w in PROFANITY_CHECK if w in combined]
    if flagged:
        errors.append("Review contains flagged content")
    return {"valid": len(errors) == 0, "errors": errors, "flagged_words": flagged}


def build_review_preview(*, rating: int, title: str, body: str, pros: list[str],
                            cons: list[str], author_name: str) -> dict:
    return {
        "rating": rating, "stars": "★" * rating + "☆" * (5 - rating),
        "title": title, "body": body[:500], "pros": pros, "cons": cons,
        "author": author_name, "date": "Today", "helpful_yes": 0, "helpful_no": 0,
    }


def get_review_guidelines() -> list[str]:
    return [
        "Be honest and specific about your experience",
        "Mention what the app does well (pros) and what could improve (cons)",
        "Avoid personal attacks or profanity",
        "Focus on the app's functionality, not pricing",
        "Include details about your use case if relevant",
    ]
