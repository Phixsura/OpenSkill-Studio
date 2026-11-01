"""Fleet DevEx Score v9 — track developer experience metrics."""
from __future__ import annotations
def fleet_devex_score_v9(teams: list[dict]) -> dict:
    avg_score = sum(t.get("devex_score", 0) for t in teams) / len(teams) if teams else 0
    build_time = sum(t.get("avg_build_sec", 0) for t in teams) / len(teams) if teams else 0
    deploy_time = sum(t.get("avg_deploy_sec", 0) for t in teams) / len(teams) if teams else 0
    return {"teams": len(teams), "avg_devex_score": round(avg_score, 1),
            "avg_build_sec": round(build_time, 1), "avg_deploy_sec": round(deploy_time, 1),
            "healthy": avg_score > 70}
