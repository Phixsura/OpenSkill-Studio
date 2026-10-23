"""Feature comparison — compare feature sets across apps or plans."""


def compare_features(*, items: list[dict], features: list[str]) -> dict:
    matrix = []
    for item in items:
        row = {"id": item["id"], "name": item["name"]}
        item_features = set(item.get("features", []))
        for feat in features:
            row[feat] = feat in item_features
        row["_count"] = sum(1 for f in features if f in item_features)
        matrix.append(row)
    matrix.sort(key=lambda r: r["_count"], reverse=True)
    winner = matrix[0] if matrix else None
    return {
        "matrix": [{k: v for k, v in row.items() if k != "_count"} for row in matrix],
        "features": features,
        "items_count": len(items),
        "winner": {"id": winner["id"], "name": winner["name"], "feature_count": winner["_count"]} if winner else None,
    }
