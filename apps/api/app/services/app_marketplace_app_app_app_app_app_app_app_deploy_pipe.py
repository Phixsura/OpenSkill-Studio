"""Deployment pipeline orchestrator — orchestrate multi-stage deploy pipelines."""
from __future__ import annotations


def run_pipeline(stages: list[dict]) -> dict:
    results = []
    for i, stage in enumerate(stages):
        fn = stage.get("fn")
        try:
            output = fn() if fn else {"ok": True}
            results.append({"stage": stage["name"], "status": "passed", "output": output})
        except Exception as e:
            results.append({"stage": stage["name"], "status": "failed", "error": str(e)})
            skipped = [{"stage": s["name"], "status": "skipped"} for s in stages[i+1:]]
            return {"success": False, "stages": results + skipped, "failed_at": stage["name"]}
    return {"success": True, "stages": results, "total": len(results)}


def pipeline_stats(runs: list[dict]) -> dict:
    successes = sum(1 for r in runs if r["success"])
    return {"total_runs": len(runs), "successes": successes,
            "failures": len(runs) - successes,
            "success_rate": round(successes / max(len(runs), 1) * 100, 1)}
