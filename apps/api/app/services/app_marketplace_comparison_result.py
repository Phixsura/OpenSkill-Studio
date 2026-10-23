"""Comparison result — generate shareable comparison results."""


def build_comparison_result(*, apps: list[dict], dimensions: list[str]) -> dict:
    if len(apps) < 2:
        return {"error": "Need at least 2 apps to compare"}
    scores = {}
    for app in apps:
        score = 0
        for dim in dimensions:
            val = app.get(dim, 0)
            if isinstance(val, (int, float)):
                score += val
        scores[app["id"]] = round(score, 1)
    winner_id = max(scores, key=scores.get)
    winner = next(a for a in apps if a["id"] == winner_id)
    return {
        "page_type": "comparison_result",
        "apps": [{"id": a["id"], "name": a["name"], "score": scores[a["id"]]} for a in apps],
        "winner": {"id": winner_id, "name": winner["name"], "score": scores[winner_id]},
        "dimensions": dimensions,
        "shareable_url": f"/marketplace/compare?apps={','.join(a['id'] for a in apps)}",
    }
