"""Marketplace report — generate monthly marketplace health report."""


def generate_monthly_report(*, month: str, new_apps: int, new_developers: int, total_installs: int,
                             top_apps: list[dict], avg_health: float) -> dict:
    return {
        "month": month,
        "new_apps": new_apps,
        "new_developers": new_developers,
        "total_installs": total_installs,
        "top_apps": top_apps[:5],
        "avg_health": round(avg_health, 1),
        "health_grade": "A" if avg_health >= 95 else "B" if avg_health >= 85 else "C" if avg_health >= 70 else "D",
    }
