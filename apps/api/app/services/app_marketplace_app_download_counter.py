"""App download counter — track SDK/bundle download stats."""

from collections import defaultdict

_downloads: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))


def record_download(app_id: str, *, version: str, platform: str = "npm") -> None:
    _downloads[app_id][f"{version}:{platform}"] += 1


def get_download_stats(app_id: str) -> dict:
    entries = _downloads.get(app_id, {})
    total = sum(entries.values())
    by_version: dict[str, int] = defaultdict(int)
    by_platform: dict[str, int] = defaultdict(int)
    for key, count in entries.items():
        version, platform = key.split(":", 1)
        by_version[version] += count
        by_platform[platform] += count
    return {"total": total, "by_version": dict(by_version), "by_platform": dict(by_platform)}
