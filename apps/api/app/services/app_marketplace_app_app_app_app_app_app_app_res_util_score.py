"""Resource utilization scorer — score resource utilization efficiency."""
from __future__ import annotations


def score_utilization(resources: list[dict]) -> dict:
    scores = []
    for r in resources:
        cpu = r.get("cpu_pct", 0)
        mem = r.get("memory_pct", 0)
        # Optimal: 40-70%. Under/over both reduce score
        cpu_score = 100 - abs(55 - cpu) * 2
        mem_score = 100 - abs(55 - mem) * 2
        avg = round((max(0, cpu_score) + max(0, mem_score)) / 2)
        status = "optimal" if avg >= 70 else ("underused" if cpu < 30 and mem < 30 else "overused")
        scores.append({"name": r["name"], "score": avg, "status": status,
                        "cpu_pct": cpu, "memory_pct": mem})
    overall = round(sum(s["score"] for s in scores) / max(len(scores), 1))
    return {"scores": sorted(scores, key=lambda s: s["score"]),
            "overall_score": overall, "resources": len(scores)}
