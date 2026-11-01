"""Fleet AI Diffusion Model — track diffusion-based generative models."""
from __future__ import annotations
def fleet_ai_diffusion(models: list[dict]) -> dict:
    active = [m for m in models if m.get("active", True)]
    generations_24h = sum(m.get("generations_24h", 0) for m in models)
    steps = round(sum(m.get("avg_steps", 0) for m in models) / max(len(models), 1))
    fid = round(sum(m.get("fid", 0) for m in models) / max(len(models), 1), 1)
    return {"models": len(models), "active": len(active), "generations_24h": generations_24h,
            "avg_steps": steps, "fid": fid, "quality": fid < 15}
