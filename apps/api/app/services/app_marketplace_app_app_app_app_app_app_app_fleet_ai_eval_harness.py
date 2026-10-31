"""Fleet AI Evaluation Harness — track model evaluation benchmarks."""
from __future__ import annotations
def fleet_ai_eval_harness(evals: list[dict]) -> dict:
    active = [e for e in evals if e.get("active", True)]
    benchmarks = sum(e.get("benchmarks", 0) for e in evals)
    runs_24h = sum(e.get("runs_24h", 0) for e in evals)
    avg_score = round(sum(e.get("score", 0) for e in evals) / max(len(evals), 1), 2)
    return {"harnesses": len(evals), "active": len(active), "benchmarks": benchmarks,
            "runs_24h": runs_24h, "avg_score": avg_score}
