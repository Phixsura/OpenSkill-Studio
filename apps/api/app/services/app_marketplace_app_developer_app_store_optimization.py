"""App Store Optimization — improve app listing discoverability."""


def analyze_listing(*, app: dict) -> dict:
    score = 0
    suggestions = []
    name = app.get("name", "")
    if 3 <= len(name) <= 30:
        score += 15
    else:
        suggestions.append("Name should be 3-30 characters")
    desc = app.get("description", "")
    if len(desc) >= 100:
        score += 20
    else:
        suggestions.append("Add a detailed description (100+ chars)")
    if app.get("icon"):
        score += 15
    else:
        suggestions.append("Add an app icon")
    screenshots = app.get("screenshots", [])
    if len(screenshots) >= 3:
        score += 15
    else:
        suggestions.append(f"Add more screenshots ({len(screenshots)}/3 minimum)")
    tags = app.get("tags", [])
    if 3 <= len(tags) <= 10:
        score += 15
    else:
        suggestions.append("Add 3-10 relevant tags")
    if app.get("documentation_url"):
        score += 10
    else:
        suggestions.append("Link to documentation")
    if app.get("support_email"):
        score += 10
    else:
        suggestions.append("Add a support email")
    return {"score": score, "max_score": 100, "suggestions": suggestions, "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"}


def suggest_keywords(*, category: str, description: str) -> list[str]:
    category_keywords = {
        "connector": ["integration", "sync", "import", "export", "connect"],
        "automation": ["workflow", "automate", "trigger", "action", "schedule"],
        "analytics": ["dashboard", "metrics", "reports", "insights", "tracking"],
    }
    base = category_keywords.get(category, ["tool", "app", "utility"])
    words = set(description.lower().split())
    relevant = [w for w in words if len(w) > 4 and w not in {"about", "which", "their", "would"}]
    return base + relevant[:5]
