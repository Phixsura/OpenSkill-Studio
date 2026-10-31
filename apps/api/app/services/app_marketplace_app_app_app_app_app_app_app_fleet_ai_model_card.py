"""Fleet AI Model Card — track model documentation and transparency."""
from __future__ import annotations
def fleet_ai_model_card(cards: list[dict]) -> dict:
    active = [c for c in cards if c.get("active", True)]
    models_documented = sum(c.get("models", 0) for c in cards)
    completeness = round(sum(c.get("completeness_pct", 0) for c in cards) / max(len(cards), 1), 1)
    sections = sum(c.get("sections", 0) for c in cards)
    return {"cards": len(cards), "active": len(active), "models": models_documented,
            "completeness": completeness, "sections": sections, "transparent": completeness > 80}
