"""Fleet Commit Analyzer v9 — track commit quality and conventional compliance."""
from __future__ import annotations
def fleet_commit_analyzer_v9(commits: list[dict]) -> dict:
    conventional = [c for c in commits if c.get("conventional")]
    signed = [c for c in commits if c.get("signed")]
    avg_size = sum(c.get("files_changed", 0) for c in commits) / len(commits) if commits else 0
    return {"total": len(commits), "conventional": len(conventional), "signed": len(signed),
            "avg_files_changed": round(avg_size, 1), "healthy": len(conventional) > len(commits) * 0.9}
