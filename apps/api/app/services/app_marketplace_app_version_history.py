"""App version history — display changelog and release timeline."""

from datetime import datetime, timedelta


def build_version_history(*, app_id: str, app_name: str) -> dict:
    base = datetime(2026, 1, 15)
    versions = []
    for i, (ver, label) in enumerate([
        ("3.2.0", "Performance improvements & dark mode"),
        ("3.1.1", "Bug fix: crash on startup with large datasets"),
        ("3.1.0", "New dashboard widgets and export options"),
        ("3.0.0", "Major redesign with new API surface"),
        ("2.5.2", "Security patch for CVE-2026-1234"),
    ]):
        dt = base - timedelta(days=i * 30)
        versions.append({
            "version": ver,
            "release_date": dt.isoformat(),
            "summary": label,
            "is_major": ver.endswith(".0.0") or ver.startswith("3.0"),
            "download_count": max(100, 5000 - i * 900),
        })
    return {
        "app_id": app_id,
        "app_name": app_name,
        "versions": versions,
        "total_versions": len(versions),
        "latest": versions[0]["version"],
    }
