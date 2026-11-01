"""Queue priority rebalancer — rebalance request queues based on load."""
from __future__ import annotations


def rebalance_queues(queues: dict[str, int], target_ratio: dict[str, float]) -> dict:
    total = sum(queues.values())
    adjustments = {}
    for name, count in queues.items():
        target = target_ratio.get(name, 1.0 / len(queues))
        actual_ratio = count / max(total, 1)
        diff = round(target - actual_ratio, 3)
        action = "increase" if diff > 0.05 else ("decrease" if diff < -0.05 else "stable")
        adjustments[name] = {"current": count, "actual_ratio": round(actual_ratio, 3),
                              "target_ratio": target, "diff": diff, "action": action}
    rebalance_needed = any(a["action"] != "stable" for a in adjustments.values())
    return {"adjustments": adjustments, "total_queued": total,
            "rebalance_needed": rebalance_needed}
