"""A/B test manager — create and evaluate split experiments."""
from __future__ import annotations
import hashlib


def create_experiment(name: str, variants: list[dict], traffic_pct: float = 100.0) -> dict:
    total_weight = sum(v.get("weight", 1) for v in variants)
    normalized = []
    for v in variants:
        w = v.get("weight", 1) / total_weight
        normalized.append({"name": v["name"], "weight": round(w * 100, 1)})
    return {"name": name, "variants": normalized, "traffic_pct": traffic_pct,
            "status": "running", "variant_count": len(normalized)}


def assign_variant(experiment: dict, user_id: str) -> str:
    h = int(hashlib.md5(f"{experiment['name']}:{user_id}".encode()).hexdigest(), 16)
    pct = (h % 10000) / 100.0
    cumulative = 0.0
    for v in experiment["variants"]:
        cumulative += v["weight"]
        if pct < cumulative:
            return v["name"]
    return experiment["variants"][-1]["name"]


def evaluate_results(variants: dict[str, dict]) -> dict:
    results = []
    best = None
    best_rate = -1
    for name, data in variants.items():
        views = data.get("views", 0)
        conversions = data.get("conversions", 0)
        rate = round(conversions / max(views, 1) * 100, 2)
        results.append({"name": name, "views": views, "conversions": conversions, "rate": rate})
        if rate > best_rate:
            best_rate = rate
            best = name
    return {"results": results, "winner": best, "best_rate": best_rate}
