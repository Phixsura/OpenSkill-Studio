"""Social proof — display trust signals for marketplace apps."""


def build_social_proof(*, app: dict) -> dict:
    installs = app.get("install_count", 0)
    rating = app.get("avg_rating", 0)
    reviews = app.get("review_count", 0)
    signals = []
    if installs >= 10000:
        signals.append({"type": "popular", "icon": "🔥", "text": f"{installs // 1000}K+ installs"})
    elif installs >= 1000:
        signals.append({"type": "growing", "icon": "📈", "text": f"{installs // 1000}K+ installs"})
    if rating >= 4.5 and reviews >= 10:
        signals.append({"type": "top_rated", "icon": "⭐", "text": f"{rating} rating ({reviews} reviews)"})
    if app.get("verified_developer"):
        signals.append({"type": "verified", "icon": "✅", "text": "Verified developer"})
    if app.get("featured"):
        signals.append({"type": "featured", "icon": "🏆", "text": "Editor's Choice"})
    if app.get("open_source"):
        signals.append({"type": "open_source", "icon": "🔓", "text": "Open source"})
    trust_score = min(len(signals) * 20, 100)
    return {"signals": signals, "trust_score": trust_score,
            "signal_count": len(signals)}
