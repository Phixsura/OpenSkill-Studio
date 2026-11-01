"""Fleet AI Model Ensemble v2 — track multi-model ensemble inference."""
from __future__ import annotations
def fleet_ai_ensemble_v2(ensembles: list[dict]) -> dict:
    active = [e for e in ensembles if e.get("active", True)]
    models_per = round(sum(e.get("models", 0) for e in ensembles) / max(len(ensembles), 1), 1)
    requests_24h = sum(e.get("requests_24h", 0) for e in ensembles)
    accuracy_boost = round(sum(e.get("boost_pct", 0) for e in ensembles) / max(len(ensembles), 1), 1)
    return {"ensembles": len(ensembles), "active": len(active), "avg_models": models_per,
            "requests_24h": requests_24h, "boost_pct": accuracy_boost, "boosted": accuracy_boost > 5}
