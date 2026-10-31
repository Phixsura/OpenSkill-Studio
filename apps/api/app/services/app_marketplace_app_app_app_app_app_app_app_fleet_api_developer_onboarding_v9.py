"""Fleet API Developer Onboarding v9 — track API dev onboarding flow."""
from __future__ import annotations
def fleet_api_developer_onboarding_v9(devs: list[dict]) -> dict:
    onboarded = [d for d in devs if d.get("onboarded")]
    activated = [d for d in devs if d.get("first_api_call")]
    avg_time = sum(d.get("onboarding_hours", 0) for d in devs) / len(devs) if devs else 0
    return {"developers": len(devs), "onboarded": len(onboarded), "activated": len(activated),
            "avg_onboarding_hours": round(avg_time, 1), "healthy": avg_time < 24}
