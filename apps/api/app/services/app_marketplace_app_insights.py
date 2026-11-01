"""App insights — AI-powered insights and recommendations for app developers."""


def generate_app_insights(*, app: dict, analytics: dict, reviews: dict,
                              health: dict) -> list[dict]:
    insights = []
    # Install velocity insight
    installs = analytics.get("installs_30d", 0)
    prev_installs = analytics.get("installs_prev_30d", 0)
    if prev_installs > 0:
        growth = round((installs - prev_installs) / prev_installs * 100, 1)
        if growth > 20:
            insights.append({"type": "positive", "icon": "📈", "title": "Install Growth",
                              "message": f"Installs up {growth}% vs last month!", "priority": 1})
        elif growth < -20:
            insights.append({"type": "warning", "icon": "📉", "title": "Install Decline",
                              "message": f"Installs down {abs(growth)}%. Consider updating your listing.", "priority": 2})
    # Review sentiment
    avg_rating = reviews.get("avg_rating", 0)
    if avg_rating < 3.5 and reviews.get("count", 0) >= 5:
        insights.append({"type": "warning", "icon": "⭐", "title": "Low Ratings",
                          "message": "Average rating below 3.5. Check recent reviews for feedback.", "priority": 1})
    # Reply rate
    reply_rate = reviews.get("reply_rate", 100)
    if reply_rate < 50:
        insights.append({"type": "action", "icon": "💬", "title": "Reply to Reviews",
                          "message": f"Only {reply_rate}% of reviews have replies. Responding boosts ratings.", "priority": 2})
    # Health
    if health.get("grade") in ("D", "F"):
        insights.append({"type": "critical", "icon": "🏥", "title": "Health Issues",
                          "message": "App health grade is low. Check error rates and response times.", "priority": 0})
    # API usage
    api_usage_pct = analytics.get("api_usage_pct", 0)
    if api_usage_pct > 80:
        insights.append({"type": "warning", "icon": "⚠️", "title": "API Quota Warning",
                          "message": f"Using {api_usage_pct}% of API quota. Consider upgrading your plan.", "priority": 1})
    if not insights:
        insights.append({"type": "positive", "icon": "✅", "title": "Looking Good!",
                          "message": "No issues detected. Keep up the great work!", "priority": 5})
    return sorted(insights, key=lambda i: i["priority"])
