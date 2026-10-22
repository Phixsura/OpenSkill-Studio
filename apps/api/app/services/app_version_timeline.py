"""Version timeline — build visual timeline of app versions."""


def build_version_timeline(versions: list[dict]) -> list[dict]:
    timeline = []
    for i, v in enumerate(versions):
        timeline.append({
            "version": v.get("version"),
            "date": v.get("created_at", ""),
            "status": v.get("review_status", "pending"),
            "changelog": v.get("changelog", ""),
            "is_latest": i == 0,
            "is_first": i == len(versions) - 1,
        })
    return timeline
