"""A/B test config — experiment variant assignment and analysis."""

import hashlib
import html


def assign_variant(*, experiment_id: str, user_id: str, variants: list[dict]) -> dict:
    total_weight = sum(v.get("weight", 1) for v in variants)
    bucket = int(hashlib.sha256(f"{experiment_id}:{user_id}".encode()).hexdigest()[:8], 16) % total_weight
    cumulative = 0
    for v in variants:
        cumulative += v.get("weight", 1)
        if bucket < cumulative:
            return {"variant": v["id"], "name": html.escape(v.get("name", v["id"])),
                    "experiment": experiment_id, "bucket": bucket}
    return {"variant": variants[-1]["id"], "name": variants[-1].get("name", ""),
            "experiment": experiment_id, "bucket": bucket}


def analyze_experiment(*, variants: list[dict]) -> dict:
    results = []
    best = None
    for v in variants:
        cr = round(v["conversions"] / max(v["impressions"], 1) * 100, 2)
        results.append({"id": v["id"], "name": html.escape(v.get("name", "")),
                         "impressions": v["impressions"], "conversions": v["conversions"],
                         "conversion_rate": cr})
        if best is None or cr > best["conversion_rate"]:
            best = results[-1]
    return {"results": results, "winner": best["id"] if best else None,
            "total_impressions": sum(v["impressions"] for v in variants)}
