"""Developer spotlight — featured developer profiles for marketplace homepage."""


def select_spotlight_developers(*, developers: list[dict], limit: int = 3) -> list[dict]:
    scored = []
    for dev in developers:
        score = (dev.get("published_apps", 0) * 10 + dev.get("total_installs", 0) / 100 +
                 dev.get("avg_rating", 0) * 20 + (50 if dev.get("verified") else 0))
        scored.append({**dev, "_score": round(score, 1)})
    return sorted(scored, key=lambda d: -d["_score"])[:limit]


def build_spotlight_card(*, developer: dict, top_apps: list[dict]) -> dict:
    return {
        "name": developer.get("display_name"), "slug": developer.get("slug"),
        "bio": developer.get("bio", "")[:120], "verified": developer.get("verified", False),
        "avatar_initial": developer.get("display_name", "?")[0],
        "stats": {"apps": developer.get("published_apps", 0),
                   "installs": developer.get("total_installs", 0),
                   "rating": developer.get("avg_rating", 0)},
        "top_apps": [{"name": a["name"], "slug": a.get("slug")} for a in top_apps[:3]],
    }
