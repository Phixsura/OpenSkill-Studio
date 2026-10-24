"""Fleet AI Reinforcement Learning — track RLHF and reward model training."""
from __future__ import annotations
def fleet_ai_rl(envs: list[dict]) -> dict:
    active = [e for e in envs if e.get("active", True)]
    episodes = sum(e.get("episodes", 0) for e in envs)
    avg_reward = round(sum(e.get("avg_reward", 0) for e in envs) / max(len(envs), 1), 2)
    convergence = round(sum(e.get("convergence", 0) for e in envs) / max(len(envs), 1), 2)
    return {"environments": len(envs), "active": len(active), "episodes": episodes,
            "avg_reward": avg_reward, "convergence": convergence, "trained": convergence > 0.9}
