"""Fleet Gitflow Tracker v9 — track branch lifecycle and merge queues."""
from __future__ import annotations
def fleet_gitflow_tracker_v9(repos: list[dict]) -> dict:
    open_prs = sum(r.get("open_prs", 0) for r in repos)
    merge_queue = sum(r.get("merge_queue", 0) for r in repos)
    stale_branches = sum(r.get("stale_branches", 0) for r in repos)
    return {"repos": len(repos), "open_prs": open_prs, "merge_queue": merge_queue,
            "stale_branches": stale_branches, "healthy": stale_branches < 10}
