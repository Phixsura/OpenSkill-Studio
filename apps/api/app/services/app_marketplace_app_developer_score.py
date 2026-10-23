"""Developer score — reputation score based on app quality and community contribution."""

def compute_developer_score(*, apps_published: int, avg_rating: float, total_installs: int,
                               reviews_replied: int, bugs_fixed: int) -> dict:
    app_score = min(25, apps_published * 5)
    rating_score = min(25, avg_rating * 5)
    popularity_score = min(25, min(total_installs, 5000) / 200)
    engagement_score = min(25, (reviews_replied + bugs_fixed) * 2)
    total = round(app_score + rating_score + popularity_score + engagement_score)
    tier = "platinum" if total >= 90 else "gold" if total >= 70 else "silver" if total >= 50 else "bronze" if total >= 25 else "newcomer"
    return {"score": total, "tier": tier, "breakdown": {"apps": round(app_score), "ratings": round(rating_score),
            "popularity": round(popularity_score), "engagement": round(engagement_score)}}
