"""User journey tracker — track user progression through funnels."""
from __future__ import annotations


def build_funnel(steps: list[str], counts: list[int]) -> dict:
    funnel = []
    for i, (step, count) in enumerate(zip(steps, counts)):
        drop_off = 0 if i == 0 else counts[i - 1] - count
        drop_pct = round(drop_off / max(counts[i - 1], 1) * 100, 1) if i > 0 else 0
        conversion = round(count / max(counts[0], 1) * 100, 1)
        funnel.append({"step": step, "count": count, "drop_off": drop_off,
                        "drop_off_pct": drop_pct, "conversion_pct": conversion})
    overall = round(counts[-1] / max(counts[0], 1) * 100, 1) if counts else 0
    return {"funnel": funnel, "steps": len(steps), "start": counts[0] if counts else 0,
            "end": counts[-1] if counts else 0, "overall_conversion": overall}


def identify_bottleneck(funnel: dict) -> dict:
    worst = max(funnel["funnel"], key=lambda s: s["drop_off_pct"]) if funnel["funnel"] else None
    return {"bottleneck": worst["step"] if worst else None,
            "drop_off_pct": worst["drop_off_pct"] if worst else 0,
            "recommendation": f"Optimize '{worst['step']}' — {worst['drop_off_pct']}% drop-off" if worst and worst["drop_off_pct"] > 0 else "No bottleneck"}
