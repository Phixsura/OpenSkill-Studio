"""Fleet engineering effectiveness — composite engineering metrics."""
from __future__ import annotations
def fleet_eng_effectiveness(metrics: dict) -> dict:
    velocity = metrics.get("velocity_pct", 0)
    quality = metrics.get("quality_pct", 0)
    delivery = metrics.get("delivery_pct", 0)
    score = round((velocity + quality + delivery) / 3, 1)
    return {"velocity": velocity, "quality": quality, "delivery": delivery,
            "score": score, "effective": score >= 75}
