"""App install analytics — track install/uninstall trends."""

from collections import defaultdict


def compute_install_trend(events: list[dict]) -> list[dict]:
    """Compute daily net installs from install/uninstall events."""
    daily: dict[str, dict] = defaultdict(lambda: {"installs": 0, "uninstalls": 0})
    for e in events:
        day = e.get("date", "")[:10]
        if e.get("type") == "install":
            daily[day]["installs"] += 1
        elif e.get("type") == "uninstall":
            daily[day]["uninstalls"] += 1
    return [{"date": d, **v, "net": v["installs"] - v["uninstalls"]} for d, v in sorted(daily.items())]


def compute_retention(installs: list[dict], uninstalls: list[dict]) -> dict:
    total = len(installs)
    churned = len(uninstalls)
    retained = total - churned
    return {"total_installs": total, "retained": retained, "churned": churned,
            "retention_rate": round(retained / total * 100, 1) if total > 0 else 100}
