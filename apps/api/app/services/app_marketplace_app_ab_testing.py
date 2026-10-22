"""A/B testing — experiment with different app listing variations."""

import hashlib


def create_experiment(*, app_id: str, name: str, variants: list[dict]) -> dict:
    if len(variants) < 2:
        return {"error": "Need at least 2 variants"}
    total_weight = sum(v.get("weight", 50) for v in variants)
    normalized = []
    for v in variants:
        normalized.append({**v, "weight_pct": round(v.get("weight", 50) / total_weight * 100, 1)})
    return {"app_id": app_id, "name": name, "variants": normalized, "status": "draft", "error": None}


def assign_variant(*, user_id: str, experiment_id: str, variants: list[dict]) -> dict:
    h = int(hashlib.md5(f"{user_id}:{experiment_id}".encode()).hexdigest(), 16)
    total = sum(v.get("weight", 50) for v in variants)
    bucket = h % total
    cumulative = 0
    for v in variants:
        cumulative += v.get("weight", 50)
        if bucket < cumulative:
            return {"variant_id": v["id"], "variant_name": v.get("name")}
    return {"variant_id": variants[-1]["id"], "variant_name": variants[-1].get("name")}


def compute_experiment_results(*, variants: list[dict]) -> dict:
    results = []
    for v in variants:
        views = v.get("views", 0)
        conversions = v.get("conversions", 0)
        rate = round(conversions / max(views, 1) * 100, 2)
        results.append({"id": v["id"], "name": v.get("name"), "views": views,
                         "conversions": conversions, "conversion_rate": rate})
    winner = max(results, key=lambda r: r["conversion_rate"]) if results else None
    return {"results": results, "winner": winner}
