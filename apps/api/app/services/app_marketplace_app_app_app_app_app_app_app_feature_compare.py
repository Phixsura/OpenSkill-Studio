"""Feature comparison matrix — compare features across plans or products."""
from __future__ import annotations


def build_comparison(products: list[dict], features: list[str]) -> dict:
    matrix = []
    for feat in features:
        row = {"feature": feat, "values": {}}
        for prod in products:
            row["values"][prod["name"]] = prod.get("features", {}).get(feat, False)
        matrix.append(row)
    scores = {}
    for prod in products:
        total = sum(1 for f in features if prod.get("features", {}).get(f, False))
        scores[prod["name"]] = {"total": total, "pct": round(total / max(len(features), 1) * 100)}
    best = max(scores, key=lambda k: scores[k]["total"]) if scores else None
    return {"products": [p["name"] for p in products], "features": features,
            "matrix": matrix, "scores": scores, "best_match": best,
            "total_features": len(features)}


def find_unique_features(products: list[dict], features: list[str]) -> dict:
    unique: dict[str, list[str]] = {p["name"]: [] for p in products}
    for feat in features:
        has = [p["name"] for p in products if p.get("features", {}).get(feat, False)]
        if len(has) == 1:
            unique[has[0]].append(feat)
    return {"unique_features": unique}
