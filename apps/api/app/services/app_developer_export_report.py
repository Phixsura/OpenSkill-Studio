"""Developer export report — generate full developer data export."""

from datetime import UTC, datetime


def build_export_report(*, developer: dict, apps: list[dict], stats: dict) -> dict:
    return {
        "export_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "developer": {k: v for k, v in developer.items() if not k.startswith("_")},
        "apps": [{k: v for k, v in a.items() if not k.startswith("_")} for a in apps],
        "stats": stats,
        "app_count": len(apps),
    }


def estimate_export_size(app_count: int, avg_manifest_kb: float = 2.0) -> dict:
    """Estimate export file size."""
    base_kb = 5  # headers + developer info
    apps_kb = app_count * (avg_manifest_kb + 1)
    total_kb = base_kb + apps_kb
    return {"estimated_kb": round(total_kb, 1), "estimated_mb": round(total_kb / 1024, 2)}
