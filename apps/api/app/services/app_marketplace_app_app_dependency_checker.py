"""Dependency checker — outdated package detection and update advisor."""

import html
import re

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _parse_ver(v: str) -> tuple[int, ...] | None:
    m = SEMVER_RE.match(v)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def check_dependencies(*, packages: list[dict]) -> dict:
    items = []
    outdated = major_updates = 0
    for pkg in packages:
        current = _parse_ver(pkg.get("current", "0.0.0"))
        latest = _parse_ver(pkg.get("latest", "0.0.0"))
        if not current or not latest:
            continue
        is_outdated = latest > current
        update_type = None
        if is_outdated:
            outdated += 1
            if latest[0] > current[0]:
                update_type = "major"
                major_updates += 1
            elif latest[1] > current[1]:
                update_type = "minor"
            else:
                update_type = "patch"
        items.append({
            "name": html.escape(pkg["name"]),
            "current": pkg["current"],
            "latest": pkg["latest"],
            "outdated": is_outdated,
            "update_type": update_type,
            "breaking": update_type == "major",
        })
    items.sort(key=lambda x: (0 if x.get("breaking") else 1, x["name"]))
    return {"packages": items, "total": len(items), "outdated": outdated,
            "major_updates": major_updates,
            "up_to_date": len(items) - outdated,
            "health": "good" if outdated == 0 else "warning" if major_updates == 0 else "critical"}
