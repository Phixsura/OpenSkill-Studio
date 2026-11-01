"""Fleet AI DPO — track direct preference optimization training."""
from __future__ import annotations
def fleet_ai_dpo(trainers: list[dict]) -> dict:
    active = [t for t in trainers if t.get("active", True)]
    pairs = sum(t.get("pairs", 0) for t in trainers)
    epochs = sum(t.get("epochs", 0) for t in trainers)
    win_rate = round(sum(t.get("win_rate", 0) for t in trainers) / max(len(trainers), 1), 1)
    return {"trainers": len(trainers), "active": len(active), "pairs": pairs,
            "epochs": epochs, "win_rate": win_rate, "aligned": win_rate > 60}
