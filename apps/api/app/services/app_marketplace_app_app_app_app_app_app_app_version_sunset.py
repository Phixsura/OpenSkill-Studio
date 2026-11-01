"""API version sunset tracker — track API versions approaching sunset."""
from __future__ import annotations


def check_sunsets(versions: list[dict]) -> dict:
    active = []
    sunsetting = []
    sunset = []
    for v in versions:
        days_left = v.get("days_until_sunset", 999)
        if days_left <= 0:
            sunset.append({**v, "status": "sunset"})
        elif days_left <= 90:
            sunsetting.append({**v, "status": "sunsetting", "days_left": days_left})
        else:
            active.append({**v, "status": "active"})
    return {"active": len(active), "sunsetting": len(sunsetting), "sunset": len(sunset),
            "total": len(versions), "action_needed": len(sunsetting) > 0 or len(sunset) > 0,
            "details": active + sunsetting + sunset}
