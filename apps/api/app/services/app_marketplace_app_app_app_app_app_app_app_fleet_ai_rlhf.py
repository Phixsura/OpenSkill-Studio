"""Fleet AI RLHF Pipeline — track reinforcement learning from human feedback."""
from __future__ import annotations
def fleet_ai_rlhf(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    comparisons = sum(p.get("comparisons", 0) for p in pipelines)
    reward_accuracy = round(sum(p.get("reward_acc", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    ppo_steps = sum(p.get("ppo_steps", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "active": len(active), "comparisons": comparisons,
            "reward_accuracy": reward_accuracy, "ppo_steps": ppo_steps, "aligned": reward_accuracy > 75}
