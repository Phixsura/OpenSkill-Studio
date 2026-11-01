"""Fleet growth rate — platform growth acceleration."""
from __future__ import annotations
def fleet_growth_rate(periods: list[dict]) -> dict:
    if len(periods) < 2:
        return {"rate": 0, "accelerating": False}
    rates = [periods[i+1].get("value", 0) - periods[i].get("value", 0) for i in range(len(periods) - 1)]
    avg_rate = round(sum(rates) / len(rates), 1)
    accel = rates[-1] > rates[0] if len(rates) >= 2 else False
    return {"avg_rate": avg_rate, "latest_rate": rates[-1], "accelerating": accel, "periods": len(periods)}
