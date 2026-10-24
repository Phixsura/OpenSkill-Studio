"""Fleet alert fatigue — measure alert noise and actionability."""
from __future__ import annotations
def fleet_alert_fatigue(alerts: list[dict]) -> dict:
    actionable = [a for a in alerts if a.get("actionable", False)]
    noise = len(alerts) - len(actionable)
    noise_pct = round(noise / max(len(alerts), 1) * 100, 1)
    return {"total": len(alerts), "actionable": len(actionable),
            "noise": noise, "noise_pct": noise_pct, "fatiguing": noise_pct > 50}
