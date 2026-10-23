"""App comparison table — side-by-side comparison of marketplace apps."""


def build_comparison_table(*, apps: list[dict], criteria: list[str]) -> dict:
    if len(apps) < 2:
        return {"error": "Need at least 2 apps to compare"}
    rows = []
    for criterion in criteria:
        row = {"criterion": criterion}
        for app in apps:
            row[app["id"]] = app.get(criterion, "—")
        rows.append(row)
    # Score each app
    scores = {}
    for app in apps:
        score = 0
        for c in criteria:
            val = app.get(c, 0)
            if isinstance(val, (int, float)):
                score += val
            elif isinstance(val, bool) and val:
                score += 10
        scores[app["id"]] = round(score, 1)
    winner_id = max(scores, key=scores.get) if scores else None
    return {
        "apps": [{"id": a["id"], "name": a["name"]} for a in apps],
        "rows": rows,
        "criteria": criteria,
        "scores": scores,
        "winner": winner_id,
    }
