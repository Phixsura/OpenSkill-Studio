"""Developer leaderboard — rank developers by activity and impact."""

def build_leaderboard(developers: list[dict], *, limit: int = 10) -> list[dict]:
    scored = []
    for dev in developers:
        score = (dev.get("app_count", 0) * 10 + dev.get("total_installs", 0) * 0.5 +
                 dev.get("avg_health", 0) * 0.2)
        scored.append({**dev, "score": round(score, 1)})
    scored.sort(key=lambda d: d["score"], reverse=True)
    return [{"rank": i + 1, **d} for i, d in enumerate(scored[:limit])]
