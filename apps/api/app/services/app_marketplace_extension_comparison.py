"""Extension Comparison — side-by-side comparison of extensions.

Compares extensions across features, pricing, ratings, installs,
performance, and generates comparison reports.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ExtensionProfile:
    extension_id: str
    name: str
    rating: float = 0.0
    installs: int = 0
    price_cents: int = 0
    features: list[str] = field(default_factory=list)
    api_count: int = 0
    avg_latency_ms: float = 0.0
    last_updated: str = ""


class ExtensionComparisonService:
    """Side-by-side extension comparison."""

    def __init__(self):
        self._profiles: dict[str, ExtensionProfile] = {}

    def register(self, extension_id: str, name: str, **kwargs) -> ExtensionProfile:
        profile = ExtensionProfile(extension_id=extension_id, name=name)
        for k, v in kwargs.items():
            if hasattr(profile, k):
                setattr(profile, k, v)
        self._profiles[extension_id] = profile
        return profile

    def compare(self, ext_ids: list[str]) -> dict:
        profiles = [self._profiles[eid] for eid in ext_ids if eid in self._profiles]
        if len(profiles) < 2:
            return {"error": "Need at least 2 extensions"}

        # Feature matrix
        all_features = set()
        for p in profiles:
            all_features.update(p.features)

        feature_matrix = {}
        for feat in sorted(all_features):
            feature_matrix[feat] = {p.extension_id: feat in p.features for p in profiles}

        # Winners per metric
        best_rating = max(profiles, key=lambda p: p.rating)
        best_installs = max(profiles, key=lambda p: p.installs)
        best_price = min(profiles, key=lambda p: p.price_cents)
        best_perf = min(profiles, key=lambda p: p.avg_latency_ms) if all(p.avg_latency_ms > 0 for p in profiles) else profiles[0]

        return {
            "extensions": [{
                "id": p.extension_id, "name": p.name, "rating": p.rating,
                "installs": p.installs, "price_cents": p.price_cents,
                "feature_count": len(p.features), "api_count": p.api_count,
                "avg_latency_ms": p.avg_latency_ms,
            } for p in profiles],
            "feature_matrix": feature_matrix,
            "winners": {
                "rating": best_rating.extension_id,
                "installs": best_installs.extension_id,
                "price": best_price.extension_id,
                "performance": best_perf.extension_id,
            },
        }

    def get_recommendation(self, ext_ids: list[str]) -> dict:
        comparison = self.compare(ext_ids)
        if "error" in comparison:
            return comparison
        # Score: rating*30 + log(installs)*20 + features*10 - price*0.1
        import math
        scores = {}
        for ext in comparison["extensions"]:
            score = (ext["rating"] * 30
                     + math.log(max(ext["installs"], 1)) * 20
                     + ext["feature_count"] * 10
                     - ext["price_cents"] * 0.001)
            scores[ext["id"]] = round(score, 1)
        best = max(scores, key=lambda k: scores[k])
        return {"recommended": best, "scores": scores}
