"""App score card — quality score breakdown for marketplace apps."""


def calculate_app_score(*, app: dict) -> dict:
    criteria = {
        "description_quality": min(len(app.get("description", "")) / 2, 20),
        "screenshots": min(app.get("screenshot_count", 0) * 5, 15),
        "documentation": 10 if app.get("has_docs") else 0,
        "testing": 10 if app.get("has_tests") else 0,
        "rating": min(app.get("avg_rating", 0) * 4, 20),
        "installs": min(app.get("install_count", 0) / 100, 10),
        "update_frequency": 10 if app.get("updated_recently") else 5 if app.get("updated_this_year") else 0,
        "support": 5 if app.get("has_support_email") else 0,
    }
    total = round(sum(criteria.values()), 1)
    grade = "A+" if total >= 90 else "A" if total >= 80 else "B" if total >= 65 else "C" if total >= 50 else "D" if total >= 30 else "F"
    return {
        "score": total,
        "grade": grade,
        "criteria": {k: round(v, 1) for k, v in criteria.items()},
        "max_score": 100,
        "improvements": [k for k, v in criteria.items() if v < 10],
    }
