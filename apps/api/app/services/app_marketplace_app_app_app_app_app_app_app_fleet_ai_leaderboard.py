"""Fleet AI Eval Leaderboard — track model comparison rankings."""
from __future__ import annotations
def fleet_ai_leaderboard(boards: list[dict]) -> dict:
    active = [b for b in boards if b.get("active", True)]
    models_ranked = sum(b.get("models", 0) for b in boards)
    benchmarks = sum(b.get("benchmarks", 0) for b in boards)
    submissions_24h = sum(b.get("submissions_24h", 0) for b in boards)
    return {"boards": len(boards), "active": len(active), "models": models_ranked,
            "benchmarks": benchmarks, "submissions_24h": submissions_24h, "competitive": models_ranked > 50}
