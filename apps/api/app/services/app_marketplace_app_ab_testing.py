"""A/B testing — run experiments on app listing variants."""

import hashlib


def create_experiment(*, app_id: str, name: str,
                       variants: list[dict]) -> dict:
    if len(variants) < 2:
        return {"error": "Need at least 2 variants"}
    total_weight = sum(v.get("weight", 50) for v in variants)
    normalized = []
    for v in variants:
        normalized.append({
            "id": v["id"],
            "name": v["name"],
            "weight": round(v.get("weight", 50) / total_weight * 100, 1),
            "impressions": 0,
            "conversions": 0,
        })
    return {
        "experiment_id": f"exp_{abs(hash(name)) % 100000:05d}",
        "app_id": app_id,
        "name": name,
        "status": "draft",
        "variants": normalized,
    }


def assign_variant(*, experiment_id: str, user_id: str,
                     variants: list[dict]) -> dict:
    h = int(hashlib.sha256(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
    idx = h % len(variants)
    return {"variant_id": variants[idx]["id"], "variant_name": variants[idx]["name"]}


def compute_results(*, variants: list[dict]) -> dict:
    results = []
    for v in variants:
        imp = v.get("impressions", 0)
        conv = v.get("conversions", 0)
        rate = round(conv / imp * 100, 2) if imp > 0 else 0.0
        results.append({"id": v["id"], "name": v["name"],
                         "impressions": imp, "conversions": conv,
                         "conversion_rate": rate})
    winner = max(results, key=lambda r: r["conversion_rate"]) if results else None
    return {"results": results, "winner": winner}
