"""User journey map — track and visualize user flows through the app."""


def build_journey_map(*, steps: list[dict]) -> dict:
    total_users = steps[0].get("users", 0) if steps else 0
    funnel = []
    for i, step in enumerate(steps):
        users = step.get("users", 0)
        drop_off = steps[i - 1].get("users", total_users) - users if i > 0 else 0
        conversion = round(users / max(total_users, 1) * 100, 1)
        funnel.append({
            "step": i + 1,
            "name": step["name"],
            "users": users,
            "drop_off": drop_off,
            "conversion_pct": conversion,
            "avg_time_sec": step.get("avg_time_sec", 0),
        })
    bottleneck = max(funnel, key=lambda f: f["drop_off"]) if funnel else None
    return {
        "steps": funnel,
        "total_steps": len(funnel),
        "start_users": total_users,
        "end_users": funnel[-1]["users"] if funnel else 0,
        "overall_conversion": funnel[-1]["conversion_pct"] if funnel else 0,
        "bottleneck": bottleneck["name"] if bottleneck and bottleneck["drop_off"] > 0 else None,
    }
